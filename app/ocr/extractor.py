import cv2
import pytesseract
import re
from app.ocr.preprocess import preprocess_image
from app.ocr.zone_config import ZONES

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def ocr_roi(image, zone, whitelist=None, psm=7):

    h, w = image.shape[:2]
    h1, h2, w1, w2 = zone

    roi = image[
        int(h*h1):int(h*h2),
        int(w*w1):int(w*w2)
    ]

    processed = preprocess_image(roi)

    config = f"--oem 3 --psm {psm}"

    if whitelist:
        config += f" -c tessedit_char_whitelist={whitelist}"

    text = pytesseract.image_to_string(
        processed,
        lang="eng",
        config=config
    )

    return text.strip()


def extract_nom(image):
    txt = ocr_roi(image, ZONES["nom"], "ABCDEFGHIJKLMNOPQRSTUVWXYZ ")
    return re.sub(r"[^A-Z ]", "", txt.upper()).strip()


def extract_prenom(image):
    txt = ocr_roi(image, ZONES["prenom"], "ABCDEFGHIJKLMNOPQRSTUVWXYZ ")
    return re.sub(r"[^A-Z ]", "", txt.upper()).strip()


def extract_nationalite(image):
    txt = ocr_roi(image, ZONES["nationalite"])
    return re.sub(r"\s+", " ", txt).strip()


def extract_date(image):
    return ocr_roi(image, ZONES["date_naissance"])


def extract_passport(image):
    txt = ocr_roi(image, ZONES["NO_passeport"], "0123456789")
    return re.sub(r"\D", "", txt)[:9]


def extract_fields(image):
    return {
        "nom": extract_nom(image),
        "prenom": extract_prenom(image),
        "nationalite": extract_nationalite(image),
        "date_naissance": extract_date(image),
        "NO_passeport": extract_passport(image)
    }