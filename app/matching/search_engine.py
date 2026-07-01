from app.matching.embedding import create_embedding
from app.matching.vector_db import search

MIN_SCORE = 70
STRONG_MATCH = 85


def cosine_to_score(distance: float):
    similarity = 1 - distance
    return round(similarity * 100, 2)


def search_passport(query, top_k=5):

    query_embedding = create_embedding(query)
    results = search(query_embedding, n_results=top_k)

    if not results["documents"] or len(results["documents"][0]) == 0:
        return []

    formatted = []

    for i in range(len(results["documents"][0])):

        doc = results["documents"][0][i]
        distance = results["distances"][0][i]
        metadata = results["metadatas"][0][i]
        print("METADATA =", metadata)   # 👈 AJOUTE ICI

        score = cosine_to_score(distance)

        if score < MIN_SCORE:
            continue

        status = "MATCH_PROBABLE" if score >= STRONG_MATCH else "A_VERIFIER"

        formatted.append({
            "id": metadata.get("passeport", ""),
            "score": score,
            "distance": round(distance, 4),
            "status": status,
            "metadata": metadata,
            "document": doc,
            "image_path": metadata.get("image_path") or (f"/data/dataset/{metadata.get('passeport')}.png" if metadata.get("passeport") else None)
        })

    return sorted(formatted, key=lambda x: x["score"], reverse=True)