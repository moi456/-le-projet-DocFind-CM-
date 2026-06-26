import os
import cv2
import csv
import re

from app.ocr.extractor import extract_fields
from app.ocr.llm_cleaner import clean_with_llm


DOSSIER_IMAGES = "data/dataset"
CSV_FILE = "passeports.csv"


# =========================
# SORTING UTILITY
# =========================
def natural_sort_key(text):
    return [
        int(c) if c.isdigit() else c.lower()
        for c in re.split(r'(\d+)', text)
    ]


# =========================
# SAVE CSV
# =========================
def save_to_csv(rows, output_file=CSV_FILE):

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow([
            "fichier", "extension",
            "nom", "prenom",
            "nationalite",
            "date_naissance",
            "NO_passeport"
        ])

        for r in rows:
            writer.writerow([
                r.get("fichier", ""),
                r.get("extension", ""),
                r.get("nom", ""),
                r.get("prenom", ""),
                r.get("nationalite", ""),
                r.get("date_naissance", ""),
                r.get("NO_passeport", "")
            ])


# =========================
# MAIN PIPELINE (IMPORTANT)
# =========================
def process_dataset(dossier=DOSSIER_IMAGES):
    """
    Lance OCR + nettoyage + export CSV
    NE S'EXÉCUTE PAS AUTOMATIQUEMENT
    """

    all_results = []

    images = sorted([
        f for f in os.listdir(dossier)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ], key=natural_sort_key)

    print(f"{len(images)} images trouvées")

    for fichier in images:

        chemin = os.path.join(dossier, fichier)
        image = cv2.imread(chemin)

        if image is None:
            continue

        # OCR extraction
        data = extract_fields(image)

        # LLM cleaning
        data = clean_with_llm(data)

        # filename metadata
        nom, ext = os.path.splitext(fichier)
        data["fichier"] = nom
        data["extension"] = ext

        all_results.append(data)

        print(fichier, "OK")

    save_to_csv(all_results)

    print("\nCSV généré :", CSV_FILE)

    return all_results