# tests/test_embedding_ollama.py

import ollama

response = ollama.embed(
    model="nomic-embed-text",
    input="ROBERT HODGE UNITED STATES OF AMERICA 15 Aug 1972 333242788"
)

vector = response["embeddings"][0]

print("Dimension :", len(vector))
print(vector[:10])