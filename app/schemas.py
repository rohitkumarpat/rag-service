from pydantic import BaseModel, Field


class TextIn(BaseModel):
    clerk_id: str
    title: str
    text: str = Field(min_length=20)


class UrlIn(BaseModel):
    clerk_id: str
    url: str

class SearchIn(BaseModel):
    clerk_id: str
    query: str = Field(min_length=2)
    k: int = Field(default=5, ge=1, le=10)



class GenerateIn(BaseModel):
    clerk_id: str
    template_prompt: str = Field(min_length=5)
    user_input: dict[str, str]
    use_knowledge: bool = True
    cite: bool = False  # True for Blog Content: adds [1], [2] markers
    k: int = Field(default=5, ge=1, le=10)