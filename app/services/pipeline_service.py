from app.services.ocr_service import extract_document
from app.services.search_service import search_documents


def run_full_pipeline(image_path: str):
    extracted = extract_document(image_path)

    if isinstance(extracted, list):
        extracted = extracted[0] if extracted else {}

    matches = search_documents(
        extracted.get("nom"),
        extracted.get("prenom"),
        extracted.get("NO_passeport"),
        extracted.get("date_naissance"),
        extracted.get("nationalite")
    )

    return {
        "extracted_data": extracted,
        "matches": matches
    }