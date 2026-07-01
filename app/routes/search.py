from fastapi import APIRouter
from app.models.requests import SearchRequest
from app.models.responses import SearchResponse
from app.services.search_service import search_documents
from app.models.responses import SearchResponse

router = APIRouter()


@router.post("/", response_model=SearchResponse)
def search_route(request: SearchRequest):
    try:
        results = search_documents(
            request.nom,
            request.prenom,
            request.numero_passeport,
            request.date_naissance,
            request.nationalite,
        )
        return {"results": results}
    except Exception as e:
        return {"error": str(e)}