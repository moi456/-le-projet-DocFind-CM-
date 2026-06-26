from fastapi import APIRouter
from app.models.requests import OCRRequest
from app.services.ocr_service import extract_document

router = APIRouter()


@router.post("/")
def ocr_route(request: OCRRequest):
    return extract_document(request.image_path)