from pydantic import BaseModel
from typing import Optional


class OCRRequest(BaseModel):
    image_path: str


class SearchRequest(BaseModel):
    nom: str
    prenom: str
    date_naissance: str
    nationalite: str
    numero_passeport: Optional[str] = None


class PipelineRequest(BaseModel):
    image_path: str