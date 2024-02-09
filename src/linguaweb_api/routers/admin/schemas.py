"""Schemas for the admin API."""
import pydantic


class Word(pydantic.BaseModel):
    """Word data, with the word itself."""

    model_config = pydantic.ConfigDict(from_attributes=True)

    id: int
    word: str
    description: str
    synonyms: list[str]
    antonyms: list[str]
    jeopardy: str
    language: str
