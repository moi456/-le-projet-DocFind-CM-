import cv2
import pytesseract
import re

# ==================================================
# CONFIG TESSERACT
# ==================================================
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# ==================================================
# OCR ROI GENERIQUE
# ==================================================
def ocr_roi(image, h1, h2, w1, w2,
            psm=7,
            whitelist=None,
            scale=4):

    h, w = image.shape[:2]

    roi = image[
        int(h*h1):int(h*h2),
        int(w*w1):int(w*w2)
    ]

    gray = cv2.cvtColor(
        roi,
        cv2.COLOR_BGR2GRAY
    )

    gray = cv2.resize(
        gray,
        None,
        fx=scale,
        fy=scale,
        interpolation=cv2.INTER_CUBIC
    )

    gray = cv2.bilateralFilter(
        gray,
        9,
        75,
        75
    )

    _, thresh = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    config = f"--oem 3 --psm {psm}"

    if whitelist:
        config += f" -c tessedit_char_whitelist={whitelist}"

    txt = pytesseract.image_to_string(
        thresh,
        lang="eng",
        config=config
    )

    return txt.strip()


# ==================================================
# EXTRACTION NOM
# ==================================================
def extract_nom(image):

    txt = ocr_roi(
        image,
        0.596, 0.620,
        0.332, 0.561,
        psm=7,
        whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ "
    )

    txt = re.sub(
        r"[^A-Z ]",
        "",
        txt.upper()
    )

    return txt.strip()


# ==================================================
# EXTRACTION PRENOM
# ==================================================
def extract_prenom(image):

    txt = ocr_roi(
        image,
        0.636, 0.661,
        0.334, 0.584,
        psm=7,
        whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ "
    )

    txt = re.sub(
        r"[^A-Z ]",
        "",
        txt.upper()
    )

    return txt.strip()


# ==================================================
# NATIONALITE
# ==================================================
def extract_nationalite(image):

    txt = ocr_roi(
        image,
        0.670, 0.698,
        0.332, 0.695,
        psm=7
    )

    txt = re.sub(
        r"\s+",
        " ",
        txt
    )

    return txt.strip()


# ==================================================
# DATE NAISSANCE
# ==================================================
def extract_date(image):

    txt = ocr_roi(
        image,
        0.710, 0.735,
        0.326, 0.590,
        psm=7
    )

    date = re.search(
        r"\d{2}\s?[A-Za-z]{3}\s?\d{4}",
        txt
    )

    return date.group() if date else txt


# ==================================================
# NUMERO PASSEPORT
# ==================================================
def extract_passport(image):

    txt = ocr_roi(
        image,
        0.564, 0.590,
        0.736, 0.916,
        psm=7,
        whitelist="0123456789"
    )

    digits = re.sub(
        r"\D",
        "",
        txt
    )

    return digits[:9]


# ==================================================
# EXTRACTION COMPLETE
# ==================================================
def extract_fields(image):

    return {

        "nom":
            extract_nom(image),

        "prenom":
            extract_prenom(image),

        "nationalite":
            extract_nationalite(image),

        "date_naissance":
            extract_date(image),

        "NO_passeport":
            extract_passport(image)
    }


# ==================================================
# PROCESS IMAGE
# ==================================================
def process_image(path):

    image = cv2.imread(path)

    if image is None:

        print("Image introuvable")

        return {}

    return extract_fields(image)


# ==================================================
# TEST
# ==================================================
if __name__ == "__main__":

    img_path = "data/dataset/28.png"

    result = process_image(img_path)

    print("\n===== RESULTAT =====\n")

    for k, v in result.items():

        print(f"{k:<20}: {v}")