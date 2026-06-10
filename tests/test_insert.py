import chromadb

from app.matching.embedding import create_embedding

client = chromadb.PersistentClient(
    path="data/chroma_db"
)

collection = client.get_or_create_collection(
    name="passeports"
)

texte = """
Nom HODGE
Prenom ROBERT
Nationalite UNITED STATES OF AMERICA
Date 15 Aug 1972
Passeport 333242788
"""

embedding = create_embedding(texte)

collection.add(
    ids=["1"],
    embeddings=[embedding],
    documents=[texte]
)

print("Passeport ajouté")
print("Total :", collection.count())