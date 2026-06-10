from app.matching.vector_db import get_collection

collection = get_collection()

data = collection.get(
    include=["documents", "metadatas"]
)

print("IDs:", data["ids"])
print("Docs:", data["documents"])
print("Meta:", data["metadatas"])