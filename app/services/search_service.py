from app.matching.search_engine import search_passport as search_similar_documents


def search_documents(nom: str, prenom: str, numero_passeport: str, date_naissance: str, nationalite: str):
    query = f"{nom} {prenom} {numero_passeport} {date_naissance} {nationalite}"
    return search_similar_documents(query)