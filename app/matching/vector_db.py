import chromadb

# ==========================================
# CLIENT CHROMADB
# ==========================================
client = chromadb.PersistentClient(path="chroma_db")


# ==========================================
# COLLECTION
# ==========================================
collection = client.get_or_create_collection(
    name="passeports"
)


# ==========================================
# GET COLLECTION (IMPORTANT)
# ==========================================
def get_collection():
    return collection


# ==========================================
# AJOUT DOCUMENT
# ==========================================
def add_document(doc_id, text, embedding, metadata=None):
    collection.add(
        ids=[doc_id],
        documents=[text],
        embeddings=[embedding],
        metadatas=[metadata or {}]
    )


# ==========================================
# RECHERCHE
# ==========================================
def search(query_embedding, n_results=5):
    return collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "distances", "metadatas"]
    )