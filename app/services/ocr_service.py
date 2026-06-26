import cv2

import os
from app.ocr.pipeline import process_dataset


def extract_document(image_path: str):

    # 🔥 rendre le chemin absolu
    full_path = os.path.join(os.getcwd(), image_path)

    image = cv2.imread(full_path)

    if image is None:
        return {
            "error": "Image introuvable",
            "received_path": image_path,
            "resolved_path": full_path
        }

    return process_dataset(image)