from app.matching.embedding import create_embedding
from app.matching.vector_db import search


# ==========================================
# CONFIGURATION
# ==========================================
MIN_SCORE = 70
STRONG_MATCH = 80


# ==========================================
# DISTANCE -> SCORE
# ==========================================
def distance_to_score(distance: float, max_distance=600):
    score = max(0, 1 - distance / max_distance)
    return round(score * 100, 2)


# ==========================================
# SEARCH ENGINE
# ==========================================
def search_passport(query, top_k=10):

    # 1. Création embedding
    query_embedding = create_embedding(query)

    # 2. Recherche ChromaDB
    results = search(query_embedding, n_results=top_k)

    if not results["documents"] or len(results["documents"][0]) == 0:
        return []

    formatted_results = []

    # 3. Traitement résultats
    for i in range(len(results["documents"][0])):

        doc = results["documents"][0][i]
        distance = results["distances"][0][i]
        metadata = results["metadatas"][0][i]

        score = distance_to_score(distance)

        # On ignore tout ce qui est < 70%
        if score < MIN_SCORE:
            continue

        # Niveau de confiance
        if score >= STRONG_MATCH:
            status = "MATCH_PROBABLE"
        else:
            status = "A_VERIFIER"

        formatted_results.append({
            "score": score,
            "distance": round(distance, 2),
            "status": status,
            "metadata": metadata,
            "document": doc
        })

    # 4. Tri décroissant
    formatted_results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return formatted_results