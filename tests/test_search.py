from app.matching.search_engine import search_passport

def run_test():

    print("\n🔍 TEST MOTEUR DE RECHERCHE PASSEPORT\n")

    query = input(
        "Entrez (nom, prénom, date, passeport...) : "
    )

    results = search_passport(query, top_k=5)

    if not results:
        print("\n❌ Aucun résultat pertinent (< 80%)")
        return

    print("\n========== RÉSULTATS ==========\n")

    for i, r in enumerate(results, start=1):

        meta = r["metadata"]

        print(f"\n===== RÉSULTAT #{i} =====")

        if r["status"] == "MATCH_PROBABLE":
            print("🔥 MATCH TRÈS PROBABLE")
        else:
            print("⚠️ À VÉRIFIER")

        print(f"Score        : {r['score']} %")
        print(f"Distance     : {r['distance']}")

        print(f"Nom          : {meta.get('nom')}")
        print(f"Prénom       : {meta.get('prenom')}")
        print(f"Nationalité  : {meta.get('nationalite')}")
        print(f"Date naissance: {meta.get('date_naissance', 'N/A')}")
        print(f"Passeport ID : {meta.get('passeport', 'N/A')}")

        print("-----------------------------")


if __name__ == "__main__":
    run_test()