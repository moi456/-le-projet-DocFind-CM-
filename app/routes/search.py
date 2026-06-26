from fastapi import APIRouter
from app.models.requests import SearchRequest
from app.services.search_service import search_documents

router = APIRouter()


@router.post("/")
def search_route(request: SearchRequest):
    try:
        return search_documents(
            request.nom,
            request.prenom,
            request.date_naissance,
            request.nationalite,
            request.numero_passeport
        )
    except Exception as e:
        return {"error": str(e)}