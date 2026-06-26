from pydantic import BaseModel


class SearchQuery(BaseModel):
    text: str