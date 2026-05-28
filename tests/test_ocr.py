import cv2
import pytesseract
import re
import os

# ─────────────────────────────────────────────
# CONFIG TESSERACT
# ─────────────────────────────────────────────
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# ─────────────────────────────────────────────
# PRETRAITEMENT IMAGE
# ─────────────────────────────────────────────
def preprocess(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh


# ─────────────────────────────────────────────
# OCR GLOBAL
# ─────────────────────────────────────────────
def extract_text(image):
    config = "--oem 3 --psm 6"
    return pytesseract.image_to_string(image, lang="eng", config=config)


# ─────────────────────────────────────────────
# NETTOYAGE OCR
# ─────────────────────────────────────────────
def clean_text(text):
    lines = text.split("\n")
    clean = []

    for l in lines:
        l = l.strip()
        if len(l) < 2:
            continue
        # On garde les longues lignes alphanumériques (MRZ) même si elles contiennent des chiffres
        if len(l) > 60 and any(c.isdigit() for c in l):
            # Ne pas supprimer les lignes qui ressemblent à la MRZ (contient P< ou <<)
            if "P<" not in l and "<<" not in l:
                continue  # supprime seulement le bruit non-MRZ
        clean.append(l)

    return clean


# ─────────────────────────────────────────────
# EXTRACTION INTELLIGENTE
# ─────────────────────────────────────────────
def extract_fields(lines):
    data = {
        "nom": "",
        "prenom": "",
        "nationalite": "",
        "date_naissance": "",
        "NO_passeport": ""      # clé unifiée
    }

    text = " ".join(lines)

    # ───── MRZ (le plus fiable)
    mrz_lines = [l for l in lines if "<<" in l]
    if mrz_lines:
        mrz = mrz_lines[-1]
        parts = mrz.split("<<")
        if len(parts) >= 2:
            data["nom"] = parts[0].replace("P<", "").replace("<", " ").strip()
            data["prenom"] = parts[1].replace("<", " ").strip()

    # ───── NATIONALITÉ
    nat = re.search(r"UNITED STATES OF AMERICA|CAMEROON|FRANCE|NIGERIA", text, re.IGNORECASE)
    if nat:
        data["nationalite"] = nat.group()

    # ───── DATE DE NAISSANCE
    date = re.search(r"\d{2}\s[A-Z][a-z]{2}\s\d{4}", text)
    if date:
        data["date_naissance"] = date.group()

    # ───── NUMÉRO PASSEPORT (9 chiffres consécutifs)
    # Cherche une séquence d'exactement 9 chiffres (ex: 776525541)
    num = re.search(r"\b\d{9}\b", text)
    if num:
        data["NO_passeport"] = num.group()

    return data


# ─────────────────────────────────────────────
# TRAITEMENT D'UNE IMAGE
# ─────────────────────────────────────────────
def process_image(path):
    image = cv2.imread(path)

    processed = preprocess(image)
    text = extract_text(processed)
    lines = clean_text(text)
    data = extract_fields(lines)

    return data


# ─────────────────────────────────────────────
# BATCH (999 IMAGES)
# ─────────────────────────────────────────────
def process_folder(folder):
    results = []

    files = [f for f in os.listdir(folder) if f.endswith((".png", ".jpg", ".jpeg"))]

    for i, file in enumerate(files, 1):
        path = os.path.join(folder, file)
        print(f"[{i}/{len(files)}] {file}")

        data = process_image(path)
        data["fichier"] = file

        results.append(data)

    return results


# ─────────────────────────────────────────────
# TEST
# ─────────────────────────────────────────────
if __name__ == "__main__":
    folder = "data/dataset/"

    results = process_folder(folder)

    print("\n===== EXEMPLE RESULTAT =====\n")
    print(results[0])