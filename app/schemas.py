from pydantic import BaseModel, Field


class TextIn(BaseModel):
    clerk_id: str
    title: str
    text: str = Field(min_length=20)


class UrlIn(BaseModel):
    clerk_id: str
    url: str