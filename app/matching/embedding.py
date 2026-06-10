# app/matching/embedding_service.py

import ollama

MODEL_NAME = "nomic-embed-text"


def create_embedding(text: str):

    response = ollama.embeddings(
        model=MODEL_NAME,
        prompt=text
    )

    return response["embedding"]