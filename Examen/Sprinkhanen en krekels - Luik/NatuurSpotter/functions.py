import requests
from bs4 import BeautifulSoup
import re

def soort_info(soort):
    headers = {"User-Agent": "Mozilla/5.0"}

    zoek_url = f"https://waarnemingen.be/search/species?q={soort.replace(' ', '%20')}"
    zoek_response = requests.get(zoek_url, headers=headers)
    zoek_soup = BeautifulSoup(zoek_response.text, "html.parser")

    soort_link = zoek_soup.find("a", href=lambda x: x and x.startswith("/species/"))
    soort_id = soort_link["href"].split("/")[2]

    detail_url = f"https://waarnemingen.be/species/{soort_id}/"
    detail_response = requests.get(detail_url, headers=headers)
    detail_soup = BeautifulSoup(detail_response.text, "html.parser")

    juiste_groep = None
    for a_tag in detail_soup.find_all("a", class_="btn btn-default btn-outline-secondary"):
        tekst = ' '.join(a_tag.text.split()).lower()
        if "sprinkhanen en krekels" in tekst:
            if a_tag.get("href") and "species_group=14" in a_tag["href"]:
                juiste_groep = a_tag
                break

    if not juiste_groep:
        print(f"⚠️ '{soort}' behoort niet tot de soortgroep 'Sprinkhanen en krekels'.")
        return

    print(f"✅ '{soort}' behoort tot de soortgroep 'Sprinkhanen en krekels'.")

    beschrijving = detail_soup.find("div", class_="description")
    beschrijving = beschrijving.text.strip() if beschrijving else "Geen beschrijving beschikbaar."

    latijn = detail_soup.find("h1")
    latijn = latijn.find("em").text.strip() if latijn and latijn.find("em") else "Onbekend"

    zeldzaam = detail_soup.find("span", class_="badge")
    zeldzaam = zeldzaam.text.strip() if zeldzaam else "Onbekend"

    afbeelding = detail_soup.find("figure")
    afbeelding_url = afbeelding.find("img")["src"] if afbeelding and afbeelding.find("img") else "Geen afbeelding gevonden"

    print(f"\nInfo over '{soort}':")
    print(f"- Latijnse naam: {latijn}")
    print(f"- Zeldzaamheidsstatus: {zeldzaam}")
    print(f"- Beschrijving: {beschrijving}")
    print(f"- Afbeelding: {afbeelding_url}")

    obs_url = f"https://waarnemingen.be/species/{soort_id}/observations/?date_after=2024-05-24&date_before=2025-05-24&country_division=22"
    obs_response = requests.get(obs_url, headers=headers)
    obs_soup = BeautifulSoup(obs_response.text, "html.parser")

    print("\n📊 10 recentste waarnemingen in Luik:")
    rijen = obs_soup.find_all("tr", class_="observation-line")
    if not rijen:
        print("Geen waarnemingen gevonden.")
        return

    for i, rij in enumerate(rijen[:10], 1):
        kolommen = rij.find_all("td")
        if len(kolommen) >= 4:
            datum = kolommen[0].text.strip()
            plaats = kolommen[1].text.strip()
            aantal = kolommen[2].text.strip()
            waarnemer = kolommen[3].text.strip()
            print(f"{i}. Datum: {datum} | Plaats: {plaats} | Aantal: {aantal} | Waarnemer: {waarnemer}")


# def observaties_kaart(dag=None):
#     print()

# def seizoensanalyse(soort, jaar):
#     print()

# def biodiversiteit_analyse(maand=None, jaar=None):
#     print()