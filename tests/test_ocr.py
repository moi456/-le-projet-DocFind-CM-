import cv2
import pytesseract
import re
import os

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# ─────────────────────────────────────────────
# PREPROCESS
# ─────────────────────────────────────────────
def preprocess(image):
    if image is None:
        return None

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU + cv2.THRESH_BINARY)
    return thresh


# ─────────────────────────────────────────────
# OCR
# ─────────────────────────────────────────────
def extract_text(image):
    return pytesseract.image_to_string(image, config="--oem 3 --psm 6")


# ─────────────────────────────────────────────
# CLEAN
# ─────────────────────────────────────────────
def clean_text(text):
    return [l.strip() for l in text.split("\n") if len(l.strip()) > 1]


# ─────────────────────────────────────────────
# PASSPORT ROI (ROBUSTE GLOBAL)
# ─────────────────────────────────────────────
def extract_passport_number(image):
    h, w = image.shape[:2]

    # ROI FIXE (TES COORDONNÉES %)
    x1, x2 = 0.738, 0.873
    y1, y2 = 0.559, 0.587

    roi = image[int(h*y1):int(h*y2), int(w*x1):int(w*x2)]

    if roi.size == 0:
        return ""

    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
    gray = cv2.GaussianBlur(gray, (3,3), 0)

    _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU + cv2.THRESH_BINARY)

    text = pytesseract.image_to_string(
        th,
        config="--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789"
    )

    digits = re.sub(r"\D", "", text)

    return digits[:9] if len(digits) >= 9 else ""


# ─────────────────────────────────────────────
# FIELD EXTRACTION
# ─────────────────────────────────────────────
def extract_fields(lines, image):
    data = {
        "nom": "",
        "prenom": "",
        "nationalite": "",
        "date_naissance": "",
        "NO_passeport": ""
    }

    text = " ".join(lines)

    # ── MRZ (simple robuste)
    mrz = [l for l in lines if "<<" in l]
    if mrz:
        parts = mrz[-1].split("<<")
        if len(parts) >= 2:
            data["nom"] = parts[0].replace("P<", "").replace("<", " ").strip()
            data["prenom"] = parts[1].replace("<", " ").strip()

    # ── NATIONALITÉ
    nat = re.search(r"UNITED STATES OF AMERICA|CAMEROON|FRANCE|NIGERIA", text, re.I)
    if nat:
        data["nationalite"] = nat.group()

    # ── DATE NAISSANCE
    date = re.search(r"\d{2}\s[A-Z][a-z]{2}\s\d{4}", text)
    if date:
        data["date_naissance"] = date.group()

    # ── PASSPORT (ROI PRIORITY)
    passport = extract_passport_number(image)

    if passport:
        data["NO_passeport"] = passport
    else:
        fallback = re.search(r"\b\d{9}\b", text)
        if fallback:
            data["NO_passeport"] = fallback.group()

    return data


# ─────────────────────────────────────────────
# PROCESS IMAGE
# ─────────────────────────────────────────────
def process_image(path):
    image = cv2.imread(path)

    if image is None:
        print(f"[ERREUR] Image introuvable: {path}")
        return {}

    processed = preprocess(image)
    if processed is None:
        return {}

    text = extract_text(processed)
    lines = clean_text(text)

    return extract_fields(lines, image)


# ─────────────────────────────────────────────
# PROCESS FOLDER
# ─────────────────────────────────────────────
def process_folder(folder):
    results = []

    files = [f for f in os.listdir(folder)
             if f.endswith((".png", ".jpg", ".jpeg"))]

    for f in files:
        path = os.path.join(folder, f)
        print("Traitement:", f)

        res = process_image(path)
        res["fichier"] = f
        results.append(res)

    return results


# ─────────────────────────────────────────────
# MAIN TEST
# ─────────────────────────────────────────────
if __name__ == "__main__":
    img_path = "data/dataset/30.png"

    result = process_image(img_path)

    print("\n===== RESULTAT =====\n")
    for k, v in result.items():
        print(f"{k:<18}: {v}")