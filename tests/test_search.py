from app.matching.search_engine import search_passport


# ==========================================
# TEST DU MOTEUR DE RECHERCHE VECTORIELLE
# ==========================================
def run_test():

    print("\n🔍 TEST RECHERCHE PASSEPORT (RAG VECTORIEL)\n")

    # Saisie utilisateur
    query = input(
        "Entrez une recherche (nom, prénom, date, passeport...) : "
    )

    # Recherche dans ChromaDB
    results = search_passport(
        query=query,
        top_k=5
    )

    # Aucun résultat
    if not results:
        print("\n❌ Aucun résultat pertinent trouvé.")
        print("Tous les résultats sont sous le seuil minimal.")
        return

    print("\n========== RÉSULTATS ==========\n")

    # Parcours des résultats
    for index, r in enumerate(results, start=1):

        meta = r["metadata"]

        print(f"\n===== RÉSULTAT #{index} =====")

        # Statut de confiance
        if r["status"] == "MATCH_PROBABLE":
            print("✅ MATCH TRÈS PROBABLE")
        else:
            print("⚠️ CORRESPONDANCE À VÉRIFIER")

        print(f"Score         : {r['score']} %")
        print(f"Distance      : {r['distance']}")

        print("\n--- Informations trouvées ---")

        print(f"Nom           : {meta.get('nom', 'N/A')}")
        print(f"Prénom        : {meta.get('prenom', 'N/A')}")
        print(f"Nationalité   : {meta.get('nationalite', 'N/A')}")
        print(f"Date naissance: {meta.get('date_naissance', 'N/A')}")
        print(f"Passeport ID  : {meta.get('passeport', 'N/A')}")

        print("\n------------------------------")


# ==========================================
# POINT D'ENTRÉE
# ==========================================
if __name__ == "__main__":
    run_test()