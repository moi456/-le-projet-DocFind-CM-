import chromadb

# ==========================================
# CLIENT CHROMADB (PERSISTENT)
# ==========================================
client = chromadb.PersistentClient(path="data/chroma_db")

# ==========================================
# COLLECTION (COSINE SIMILARITY)
# ==========================================
collection = client.get_or_create_collection(
    name="passeports",
    metadata={
        "hnsw:space": "cosine"
    }
)

# ==========================================
# GET COLLECTION
# ==========================================
def get_collection():
    return collection

# ==========================================
# ADD DOCUMENT
# ==========================================
def add_document(doc_id, text, embedding, metadata=None):
    collection.add(
        ids=[doc_id],
        documents=[text],
        embeddings=[embedding],
        metadatas=[metadata or {}]
    )

# ==========================================
# SEARCH
# ==========================================
def search(query_embedding, n_results=5):
    return collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "distances", "metadatas"]
    )