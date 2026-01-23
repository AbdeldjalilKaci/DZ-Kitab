# scraper_cursus.py
import requests
from bs4 import BeautifulSoup
import pandas as pd

def main():
    # ⚠️ Remplace cette URL par celle du site que tu veux scraper
    url = "URL_DU_SITE_DES_CURSUS"

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    cursus_list = []

    # ⚠️ Remplace ce selector par la balise CSS qui contient les cursus
    for item in soup.select("SELECTEUR_HTML_DU_CURSUS"):
        nom = item.text.strip()
        cursus_list.append({
            "nom_cursus": nom
        })

    # Sauvegarder dans CSV
    df = pd.DataFrame(cursus_list)
    df.to_csv("cursus_universitaires.csv", index=False)
    print("✅ Scraping terminé, CSV créé !")

if __name__ == "__main__":
    main()
