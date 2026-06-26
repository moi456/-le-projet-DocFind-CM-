from pydantic import BaseModel


class Document(BaseModel):
    id: str
    nom: str
    prenom: str
    numero_passeport: str
    image_path: str