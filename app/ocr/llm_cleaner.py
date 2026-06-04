import re
import json
import ollama

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

    for k, v in corrections.items():
        date = date.replace(k, v)

    date = re.sub(r"\s+", " ", date)

    match = re.search(r"\d{1,2}\s[A-Za-z]{3}\s\d{4}", date)

    return match.group() if match else date


def clean_with_llm(data):

    preclean = {
        "nom": data["nom"],
        "prenom": data["prenom"],
        "nationalite": data["nationalite"],
        "date_naissance": fix_date(data["date_naissance"]),
        "NO_passeport": data["NO_passeport"]
    }

    try:
        response = ollama.chat(
            model="llama3.2:latest",
            messages=[{
                "role": "user",
                "content": f"Retourne uniquement JSON:\n{json.dumps(preclean)}"
            }],
            options={"temperature": 0}
        )

        txt = response["message"]["content"]

        m = re.search(r"\{.*\}", txt, re.DOTALL)

        if m:
            return json.loads(m.group())

    except:
        pass

    return preclean