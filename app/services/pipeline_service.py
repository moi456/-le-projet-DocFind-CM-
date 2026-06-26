from app.services.ocr_service import extract_document
from app.services.search_service import search_documents


def run_full_pipeline(image_path: str):
    extracted = extract_document(image_path)

    matches = search_documents(
        extracted["nom"],
        extracted["prenom"],
        extracted["numero_passeport"]
    )

    return {
        "extracted_data": extracted,
        "matches": matches
    }