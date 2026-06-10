import cv2
import pytesseract
import re
import csv
import os
import json
import ollama

# ==========================================
# CONFIG
# ==========================================
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

DOSSIER_IMAGES = "data/dataset"
CSV_FILE = "passeports.csv"

# ==========================================
# TRI NATUREL
# 1.png 2.png 10.png
# ==========================================
def natural_sort_key(text):

    return [

        int(c) if c.isdigit() else c.lower()

        for c in re.split(r'(\d+)', text)

    ]


# ==========================================
# OCR ROI
# ==========================================
def ocr_roi(
        image,
        h1,h2,w1,w2,
        psm=7,
        whitelist=None,
        scale=4
):

    h,w = image.shape[:2]

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

    _,thresh = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY+cv2.THRESH_OTSU
    )

    config = f"--oem 3 --psm {psm}"

    if whitelist:

        config += (
            f" -c tessedit_char_whitelist="
            f"{whitelist}"
        )

    txt = pytesseract.image_to_string(

        thresh,

        lang="eng",

        config=config

    )

    return txt.strip()


# ==========================================
# EXTRACTIONS
# ==========================================
def extract_nom(image):

    txt = ocr_roi(

        image,

        0.596,0.620,

        0.332,0.561,

        whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ "

    )

    return re.sub(

        r"[^A-Z ]",

        "",

        txt.upper()

    ).strip()


def extract_prenom(image):

    txt = ocr_roi(

        image,

        0.636,0.661,

        0.334,0.584,

        whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ "

    )

    return re.sub(

        r"[^A-Z ]",

        "",

        txt.upper()

    ).strip()


def extract_nationalite(image):

    txt = ocr_roi(

        image,

        0.670,0.698,

        0.332,0.695

    )

    return re.sub(

        r"\s+",

        " ",

        txt

    ).strip()


def extract_date(image):

    txt = ocr_roi(

        image,

        0.710,0.735,

        0.326,0.590

    )

    return txt.strip()


def extract_passport(image):

    txt = ocr_roi(

        image,

        0.564,0.590,

        0.736,0.916,

        whitelist="0123456789"

    )

    return re.sub(

        r"\D",

        "",

        txt

    )[:9]


# ==========================================
# EXTRACTION COMPLETE
# ==========================================
def extract_fields(image):

    return {

        "nom": extract_nom(image),

        "prenom": extract_prenom(image),

        "nationalite": extract_nationalite(image),

        "date_naissance": extract_date(image),

        "NO_passeport": extract_passport(image)

    }


# ==========================================
# CLEAN DATE
# ==========================================
def fix_date(date):

    date = str(date)

    corrections = {

        "IS ": "15 ",

        "I5 ": "15 ",

        "l5 ": "15 ",

        "Ol ": "01 ",

        "O1 ": "01 ",

        "O2 ": "02 ",

        "]": "",

        "[": ""

    }

    for k,v in corrections.items():

        date = date.replace(

            k,

            v

        )

    date = re.sub(

        r"\s+",

        " ",

        date

    )

    match = re.search(

        r"\d{1,2}\s[A-Za-z]{3}\s\d{4}",

        date

    )

    return match.group() if match else date


# ==========================================
# OLLAMA
# ==========================================
def clean_with_llm(data):

    preclean = {

        "nom": data["nom"],

        "prenom": data["prenom"],

        "nationalite": data["nationalite"],

        "date_naissance": fix_date(

            data["date_naissance"]

        ),

        "NO_passeport": data["NO_passeport"]

    }

    try:

        response = ollama.chat(

            model="llama3.2:latest",

            messages=[

                {

                    "role":"user",

                    "content":

                    f"Retourne uniquement JSON:\n"

                    f"{json.dumps(preclean)}"

                }

            ],

            options={

                "temperature":0,

                "num_predict":50

            }

        )

        txt = response["message"]["content"]

        m = re.search(

            r"\{.*\}",

            txt,

            re.DOTALL

        )

        if m:

            return json.loads(

                m.group()

            )

    except:

        pass

    return preclean


# ==========================================
# CSV
# ==========================================
def save_to_csv(rows):

    with open(

        CSV_FILE,

        "w",

        newline="",

        encoding="utf-8"

    ) as f:

        writer = csv.writer(f)

        writer.writerow([

            "fichier",

            "extension",

            "nom",

            "prenom",

            "nationalite",

            "date_naissance",

            "NO_passeport"

        ])

        for row in rows:

            writer.writerow([

                row["fichier"],

                row["extension"],

                row["nom"],

                row["prenom"],

                row["nationalite"],

                row["date_naissance"],

                row["NO_passeport"]

            ])


# ==========================================
# MAIN
# ==========================================
all_results = []

images = sorted(

    [

        f for f in os.listdir(

            DOSSIER_IMAGES

        )

        if f.lower().endswith(

            (".png",".jpg",".jpeg")

        )

    ],

    key=natural_sort_key

)

print(

    f"{len(images)} images trouvées"

)

for fichier in images:

    chemin = os.path.join(

        DOSSIER_IMAGES,

        fichier

    )

    image = cv2.imread(

        chemin

    )

    if image is None:

        continue

    data = extract_fields(

        image

    )

    data = clean_with_llm(

        data

    )

    nom, ext = os.path.splitext(

        fichier

    )

    data["fichier"] = nom
    data["extension"] = ext

    all_results.append(

        data

    )

    print(

        fichier,

        "OK"

    )

save_to_csv(

    all_results

)

print(

    "\nCSV généré :", CSV_FILE

)
