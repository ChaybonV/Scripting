import requests
from bs4 import BeautifulSoup
import re

def soort_info(soort):
    zoek_url = f"https://waarnemingen.be/species/search/?q={soort.replace(' ', '%20')}"
    zoek_response = requests.get(zoek_url)
    zoek_soup = BeautifulSoup(zoek_response.content, 'html.parser')

    soort_id = None
    rows = zoek_soup.find_all("tr")
    for row in rows:
        naam = row.find("span", class_="species-common-name")
        if naam.text.strip().lower() == soort.lower():
            link = row.find("a", href=True)
            if link:
                match = re.search(r'/species/(\d+)/', link['href'])
                if match:
                    soort_id = match.group(1)
                    break

    url_info = f"https://waarnemingen.be/species/{soort_id}/"
    response_info = requests.get(url_info)
    soup_info = BeautifulSoup(response_info.content, 'html.parser')

    latijnse_naam = "Onbekend"
    subtitle_div = soup_info.find("div", class_="species-subtitle")
    if subtitle_div:
        a_tag = subtitle_div.find("a")
        if a_tag:
            i_tag = a_tag.find("i", class_="species-scientific-name")
            if i_tag:
                latijnse_naam = i_tag.text.strip()

    content_div = soup_info.find("div", class_="app-content-section js-user-content")
    if content_div:
        paragrafen = content_div.find_all("p")
        beschrijving = "\n\n".join(p.text.strip() for p in paragrafen)
    else:
        beschrijving = "Geen beschrijving gevonden."

    afbeelding_tag = soup_info.find("img")
    afbeelding_url = afbeelding_tag['src'] if afbeelding_tag else "Geen afbeelding beschikbaar."

    url_stats = f"https://waarnemingen.be/species/{soort_id}/statistics/"
    response_stats = requests.get(url_stats)
    soup_stats = BeautifulSoup(response_stats.content, 'html.parser')

    print(f"\n{soort}\n")
    print(f"[Afbeelding]: {afbeelding_url}")
    print(f"Latijnse naam: {latijnse_naam}")
    #print(f"Zeldzaamheidstatus: {status}")
    print("\nBeschrijving:\n")
    print(beschrijving)



def observaties_kaart(dag=None):
    print()

def seizoensanalyse(soort, jaar):
    print()

def biodiversiteit_analyse(maand=None, jaar=None):
    print()