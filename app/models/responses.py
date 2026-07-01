from pydantic import BaseModel
from typing import List, Optional


class OCRResponse(BaseModel):
    nom: str
    prenom: str
    numero_passeport: str
    confidence: float


class SearchResult(BaseModel):
    id: str
    score: float
    image_path: Optional[str] = None


class SearchResponse(BaseModel):
    results: List[SearchResult]


class PipelineResponse(BaseModel):
    extracted_data: dict
    matches: List[SearchResult]