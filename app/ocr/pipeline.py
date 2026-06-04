import os
import cv2
import csv
import re

from app.ocr.extractor import extract_fields
from app.ocr.llm_cleaner import clean_with_llm


DOSSIER_IMAGES = "data/dataset"
CSV_FILE = "passeports.csv"


def natural_sort_key(text):
    return [
        int(c) if c.isdigit() else c.lower()
        for c in re.split(r'(\d+)', text)
    ]


def save_to_csv(rows):

    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:

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
                r["fichier"], r["extension"],
                r["nom"], r["prenom"],
                r["nationalite"],
                r["date_naissance"],
                r["NO_passeport"]
            ])


all_results = []

images = sorted([
    f for f in os.listdir(DOSSIER_IMAGES)
    if f.lower().endswith((".png", ".jpg", ".jpeg"))
], key=natural_sort_key)

print(f"{len(images)} images trouvées")

for fichier in images:

    chemin = os.path.join(DOSSIER_IMAGES, fichier)
    image = cv2.imread(chemin)

    if image is None:
        continue

    data = extract_fields(image)
    data = clean_with_llm(data)

    nom, ext = os.path.splitext(fichier)
    data["fichier"] = nom
    data["extension"] = ext

    all_results.append(data)

    print(fichier, "OK")

save_to_csv(all_results)

print("\nCSV généré :", CSV_FILE)