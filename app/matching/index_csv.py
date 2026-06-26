import csv
import os
import shutil

from app.matching.embedding import create_embedding
from app.matching.vector_db import client

# ==========================================
# CONFIG
# ==========================================
CSV_PATH = "passeports.csv"
DB_PATH = "chroma_db"
COLLECTION_NAME = "passeports"


# ==========================================
# RESET CHROMA DB
# ==========================================
def reset_chroma():
    if os.path.exists(DB_PATH):
        try:
            shutil.rmtree(DB_PATH)
            print("🧹 Base Chroma supprimée")
        except PermissionError:
            print("❌ Ferme Uvicorn / Python et réessaie.")


# ==========================================
# COLLECTION
# ==========================================
def get_collection():
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )


# ==========================================
# TEXT FOR EMBEDDING
# ==========================================
def row_to_text(row):
    return f"""
Nom: {row.get('nom', '')}
Prenom: {row.get('prenom', '')}
Nationalite: {row.get('nationalite', '')}
Date_naissance: {row.get('date_naissance', '')}
Passeport: {row.get('NO_passeport', '')}
""".strip()



# ==========================================
# INDEXATION
# ==========================================
def index_csv():
    print("📥 Lecture du CSV...")

    if not os.path.exists(CSV_PATH):
        print("❌ CSV introuvable :", CSV_PATH)
        return

    collection = get_collection()  # 🔥 IMPORTANT ICI

    with open(CSV_PATH, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        count = 0

        for row in reader:
            try:
                text = row_to_text(row)
                vector = create_embedding(text)

                doc_id = row.get("NO_passeport")

                if not doc_id:
                    continue

      

                metadata = {
    "nom": row.get("nom", ""),
    "prenom": row.get("prenom", ""),
    "nationalite": row.get("nationalite", ""),
    "date_naissance": row.get("date_naissance", ""),
    "passeport": doc_id,
    "image_path": f"/data/dataset/{doc_id}.png" if doc_id else None
}
                print("DEBUG METADATA:", metadata)
                collection.add(
                    ids=[doc_id],
                    documents=[text],
                    embeddings=[vector],
                    metadatas=[metadata]
                )

                count += 1
                print(f"✔ Indexé: {doc_id}")

            except Exception as e:
                print(f"⚠ Erreur ligne {row}: {e}")

    print(f"\n🚀 Terminé ! {count} passeports indexés.")


# ==========================================
# MAIN
# ==========================================
if __name__ == "__main__":
    reset_chroma()
    index_csv()