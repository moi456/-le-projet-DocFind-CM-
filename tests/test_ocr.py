import cv2
import pytesseract
import re
import csv
import os
import ollama
import json

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
# EXTRACTION COMPLETE
## ==================================================
# NETTOYAGE OCR + OLLAMA
# ==================================================
def clean_with_llm(data):

    # -------------------------
    # PRE CLEAN
    # -------------------------
    preclean = {

        "nom": re.sub(
            r"[^A-Z ]",
            "",
            str(data.get("nom", "")).upper()
        ).strip(),

        "prenom": re.sub(
            r"[^A-Z ]",
            "",
            str(data.get("prenom", "")).upper()
        ).strip(),

        "nationalite": re.sub(
            r"\s+",
            " ",
            str(data.get(
                "nationalite",
                ""
            ))
        ).strip(),

        "date_naissance": str(
            data.get(
                "date_naissance",
                ""
            )
        ),

        "NO_passeport": re.sub(
            r"\D",
            "",
            str(
                data.get(
                    "NO_passeport",
                    ""
                )
            )
        )[:9]
    }

    # -------------------------
    # REGEX CLEAN DATE
    # -------------------------
    date = preclean["date_naissance"]

    date = date.replace(
        "]",
        ""
    )

    date = date.replace(
        "[",
        ""
    )

    date = date.replace(
        "IS ",
        "15 "
    )

    date = date.replace(
        "I5 ",
        "15 "
    )

    date = date.replace(
        "l5 ",
        "15 "
    )

    date = re.sub(
        r"\s+",
        " ",
        date
    )

    preclean["date_naissance"] = date

    prompt = f"""
Corrige seulement les erreurs OCR évidentes.

Retourne STRICTEMENT un JSON.

Format obligatoire :

{{
"nom":"",
"prenom":"",
"nationalite":"",
"date_naissance":"",
"NO_passeport":""
}}

DONNEES :

{json.dumps(preclean)}
"""

    try:

        response = ollama.chat(

            model="llama3.2:latest",

            messages=[

                {
                    "role": "user",
                    "content": prompt
                }

            ],

            options={

                "temperature": 0,

                "num_predict": 80

            }

        )

        text = response["message"]["content"]

        print("\nDEBUG OLLAMA:")
        print(text)

        match = re.search(

            r"\{.*\}",

            text,

            re.DOTALL

        )

        if not match:

            print(
                "JSON introuvable -> OCR utilisé"
            )

            return preclean

        cleaned = json.loads(

            match.group()

        )

        cleaned["nom"] = re.sub(

            r"[^A-Z ]",

            "",

            str(
                cleaned.get(
                    "nom",
                    preclean["nom"]
                )
            ).upper()

        ).strip()

        cleaned["prenom"] = re.sub(

            r"[^A-Z ]",

            "",

            str(
                cleaned.get(
                    "prenom",
                    preclean["prenom"]
                )
            ).upper()

        ).strip()

        cleaned["nationalite"] = re.sub(

            r"\s+",

            " ",

            str(
                cleaned.get(
                    "nationalite",
                    preclean["nationalite"]
                )
            )

        ).strip()

        cleaned["NO_passeport"] = re.sub(

            r"\D",

            "",

            str(
                cleaned.get(
                    "NO_passeport",
                    preclean["NO_passeport"]
                )
            )

        )[:9]

        date = str(

            cleaned.get(

                "date_naissance",

                preclean[
                    "date_naissance"
                ]

            )

        )

        match = re.search(

            r"\d{1,2}\s[A-Za-z]{3}\s\d{4}",

            date

        )

        cleaned["date_naissance"] = (

            match.group()

            if match

            else preclean[
                "date_naissance"
            ]

        )

        return cleaned

    except Exception as e:

        print(

            "\nOllama ignoré :",

            e

        )

        return preclean
# ==================================================
# PROCESS IMAGE
# ==================================================
def process_image(path):

    image = cv2.imread(path)

    if image is None:

        print("Image introuvable")

        return {}

    raw_data = extract_fields(image)

    clean_data = clean_with_llm(raw_data)

    return clean_data
    
# ==================================================
# SAUVEGARDE CSV
# ==================================================

def save_to_csv(data, filename="passeports.csv"):

    file_exists = os.path.isfile(
        filename
    )

    with open(
        filename,
        mode="a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(
            file
        )

        # écrire entêtes seulement
        # si fichier inexistant
        if not file_exists:

            writer.writerow([

                "nom",
                "prenom",
                "nationalite",
                "date_naissance",
                "NO_passeport"

            ])

        writer.writerow([

            data["nom"],
            data["prenom"],
            data["nationalite"],
            data["date_naissance"],
            data["NO_passeport"]

        ])

    print(
        f"\nDonnées sauvegardées dans {filename}"
    )


# ==================================================
# TEST
# ==================================================
if __name__ == "__main__":

    img_path = "data/dataset/41.png"

    result = process_image(
        img_path
    )

    print("\n===== RESULTAT =====\n")

    for k, v in result.items():

        print(
            f"{k:<20}: {v}"
        )

    save_to_csv(
        result
    )