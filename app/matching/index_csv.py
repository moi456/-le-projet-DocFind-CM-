import csv
import os
import shutil
from app.matching.embedding import create_embedding
from app.matching.vector_db import get_collection

# ==========================================
# CONFIG
# ==========================================
CSV_PATH = "passeports.csv"
DB_PATH = "chroma_db"

collection = get_collection()

# ==========================================
# RESET CHROMA DB
# ==========================================
def reset_chroma():
    db_path = "chroma_db"

    if os.path.exists(db_path):
        try:
            shutil.rmtree(db_path)
            print("🧹 Base supprimée")
        except PermissionError:
            print("❌ Base utilisée. Ferme Python et réessaie.")

# ==========================================
# TEXTE POUR EMBEDDING
# ==========================================
def row_to_text(row):
    return f"""
Nom: {row['nom']}
Prenom: {row['prenom']}
Nationalite: {row['nationalite']}
Date_naissance: {row['date_naissance']}
Passeport: {row['NO_passeport']}
""".strip()

# ==========================================
# INDEXATION
# ==========================================
def index_csv():
    print("📥 Lecture du CSV...")

    with open(CSV_PATH, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        count = 0

        for row in reader:

            text = row_to_text(row)
            vector = create_embedding(text)

            doc_id = row["NO_passeport"]

            metadata = {
                "nom": row["nom"],
                "prenom": row["prenom"],
                "nationalite": row["nationalite"],
                "date_naissance": row["date_naissance"],
                "passeport": row["NO_passeport"]
            }

            collection.add(
                ids=[doc_id],
                documents=[text],
                embeddings=[vector],
                metadatas=[metadata]
            )

            count += 1
            print(f"✔ Indexé: {doc_id}")

    print(f"\n🚀 Terminé ! {count} passeports indexés.")

# ==========================================
# MAIN
# ==========================================
if __name__ == "__main__":
    reset_chroma()
    index_csv()