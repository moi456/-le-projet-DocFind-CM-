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
        if len(l) > 60 and any(c.isdigit() for c in l):
            if "P<" not in l and "<<" not in l:
                continue
        clean.append(l)

    return clean


# ─────────────────────────────────────────────
# EXTRACTION ZONE NUMÉRO PASSEPORT
# ─────────────────────────────────────────────
def extraire_numero_zone(image_originale):
    """
    Extraction robuste du numéro de passeport via ROI fixe
    """

    h, w = image_originale.shape[:2]

    # ROI (TES COORDONNÉES %)
    x1, x2 = 0.738, 0.873
    y1, y2 = 0.559, 0.587

    roi = image_originale[
        int(h * y1):int(h * y2),
        int(w * x1):int(w * x2)
    ]

    if roi.size == 0:
        return ""

    # ── Amélioration OCR (IMPORTANT)
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    # upscale plus fort (important pour chiffres fins)
    gray = cv2.resize(gray, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)

    # suppression bruit
    gray = cv2.bilateralFilter(gray, 9, 75, 75)

    # binarisation plus stable que OTSU seul
    _, thresh = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # OCR très strict chiffres
    config = "--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789"

    text = pytesseract.image_to_string(thresh, config=config)

    # nettoyage
    digits = re.sub(r"\D", "", text)

    # sécurité : parfois OCR lit moins → on complète si besoin
    if len(digits) < 9:
        # fallback OCR brut (IMPORTANT)
        config2 = "--oem 3 --psm 6"
        text2 = pytesseract.image_to_string(roi, config=config2)
        digits2 = re.sub(r"\D", "", text2)
        digits = digits if len(digits) > len(digits2) else digits2

    return digits[:9] if len(digits) >= 9 else ""


# ─────────────────────────────────────────────
# EXTRACTION INTELLIGENTE
# ─────────────────────────────────────────────
def extract_fields(lines, image_originale):
    data = {
        "nom"           : "",
        "prenom"        : "",
        "nationalite"   : "",
        "date_naissance": "",
        "NO_passeport"  : ""
    }

    text = " ".join(lines)

    # ───── MRZ
    mrz_lines = [l for l in lines if "<<" in l]
    if mrz_lines:
        mrz = mrz_lines[-1]
        parts = mrz.split("<<")
        if len(parts) >= 2:
            data["nom"]    = parts[0].replace("P<", "").replace("<", " ").strip()
            data["prenom"] = parts[1].replace("<", " ").strip()

    # ───── NATIONALITÉ
    nat = re.search(
        r"UNITED STATES OF AMERICA|CAMEROON|FRANCE|NIGERIA",
        text, re.IGNORECASE
    )
    if nat:
        data["nationalite"] = nat.group()

    # ───── DATE DE NAISSANCE
    date = re.search(r"\d{2}\s[A-Z][a-z]{2}\s\d{4}", text)
    if date:
        data["date_naissance"] = date.group()

    # ───── NUMÉRO PASSEPORT — zone ciblée
    numero = extraire_numero_zone(image_originale)
    if len(numero) == 9:
        data["NO_passeport"] = numero
    else:
        # Fallback regex
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
    data = extract_fields(lines, image)
    return data


# ─────────────────────────────────────────────
# BATCH (999 IMAGES)
# ─────────────────────────────────────────────
def process_folder(folder):
    results = []

    files = [f for f in os.listdir(folder)
             if f.endswith((".png", ".jpg", ".jpeg"))]

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
    img_path = "data/dataset/30.png"

    result = process_image(img_path)

    print("\n===== RESULTAT =====\n")

    for cle, val in result.items():
        print(f"  {cle:<20} : {val}")