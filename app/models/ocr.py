from typing import Optional
from pydantic import BaseModel

class OCRData(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    numero_passeport: Optional[str] = None
    date_naissance: Optional[str] = None
    nationalite: Optional[str] = None