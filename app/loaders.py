import io
import ipaddress
import socket
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from pypdf import PdfReader

HEADERS = {"User-Agent": "Mozilla/5.0 (BrandKnowledgeBot)"}


def load_pdf(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))
    return "\n\n".join((p.extract_text() or "") for p in reader.pages)


def load_txt(data: bytes) -> str:
    return data.decode("utf-8", errors="ignore")


def _check_public(url: str):
    # block localhost / private networks (SSRF protection)
    u = urlparse(url)
    if u.scheme not in ("http", "https") or not u.hostname:
        raise ValueError("Invalid URL")
    for info in socket.getaddrinfo(u.hostname, None):
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            raise ValueError("URL not allowed")


def load_url(url: str) -> tuple[str, str]:
    for _ in range(4):  # follow up to 3 redirects, checking each hop
        _check_public(url)
        r = httpx.get(url, timeout=15, headers=HEADERS)
        if r.is_redirect:
            url = str(r.next_request.url)
            continue
        break
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.decompose()
    title = soup.title.get_text(strip=True) if soup.title else url
    return title, soup.get_text("\n")