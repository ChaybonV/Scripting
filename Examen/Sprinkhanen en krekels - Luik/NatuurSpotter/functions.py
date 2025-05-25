import requests
from bs4 import BeautifulSoup
from datetime import date

def soort_info(soort):
    zoek_url = f"https://waarnemingen.be/search/?q={soort.replace(' ', '+')}"
    zoek_resp = requests.get(zoek_url)
    if zoek_resp.status_code != 200:
        print("Fout bij ophalen van zoekpagina.")
        return

    zoek_soup = BeautifulSoup(zoek_resp.text, "html.parser")
    lijstitem = zoek_soup.find("li", class_="lead")
    if not lijstitem:
        print("Soort niet gevonden.")
        return

    a_tag = lijstitem.find("a", href=True)
    if not a_tag or "/species/" not in a_tag["href"]:
        print("Soortlink niet gevonden.")
        return

    href = a_tag["href"]
    soort_id = href.strip("/").split("/")[-1]
    soort_url = f"https://waarnemingen.be{href}"

    resp = requests.get(soort_url)
    if resp.status_code != 200:
        print("Fout bij openen van soortpagina.")
        return

    soup = BeautifulSoup(resp.text, "html.parser")

    soortgroep_link = soup.find("a", href="/species/search/?species_group=14")
    if not soortgroep_link:
        print("❌ Deze soort behoort niet tot de soortgroep 'Sprinkhanen en krekels'.")
        return

    beschrijving_div = soup.find("div", class_="app-content-section js-user-content")
    beschrijving = beschrijving_div.get_text().strip() if beschrijving_div else "Geen beschrijving gevonden."

    latijn_tag = soup.find("i", class_="species-scientific-name")
    latijnse_naam = latijn_tag.text.strip() if latijn_tag else "Onbekend"

    status_span = soup.find("span", class_="hidden-sm")
    status = status_span.text.strip() if status_span else "Niet vermeld"

    afbeelding_tag = soup.find("figure", class_="app-ratio-box-4-3 lightbox-gallery")
    img = afbeelding_tag.find("img") if afbeelding_tag else None
    afbeelding_url = "https://waarnemingen.be" + img["src"] if img else "Geen afbeelding gevonden"

    vandaag = date.today()
    vorig_jaar = vandaag.replace(year=vandaag.year - 1)
    obs_url = (f"https://waarnemingen.be/species/{soort_id}/observations/"f"?date_after={vorig_jaar}&date_before={vandaag}&country_division=22")
    obs_resp = requests.get(obs_url)
    if obs_resp.status_code != 200:
        print("Fout bij ophalen van waarnemingen.")
        return

    obs_soup = BeautifulSoup(obs_resp.text, "html.parser")
    tbody = obs_soup.find("tbody")
    observaties = []

    if tbody:
        rijen = tbody.find_all("tr", class_=["even", "odd"])
        for rij in rijen[:10]:
            kolommen = rij.find_all("td")
            if len(kolommen) >= 3:
                datum = kolommen[0].text.strip()
                aantal_raw = kolommen[1].get_text(separator=" ").strip()
                aantal = aantal_raw.split()[0] if aantal_raw else "?"
                locatie = kolommen[2].text.strip()
                observaties.append((datum, aantal, locatie))

    print(f"\nInfo over '{soort}':")
    print(f"Latijnse naam: {latijnse_naam}")
    print(f"Zeldzaamheidsstatus: {status}")
    print(f"Beschrijving:\n{beschrijving}")
    print(f"Afbeelding: {afbeelding_url}\n")

    print(f"10 recentste waarnemingen in provincie Luik (tussen {vorig_jaar} en {vandaag}):")
    if not observaties:
        print("Geen waarnemingen gevonden.")
    else:
        for datum, aantal, locatie in observaties:
            print(f"{datum} - {aantal} - {locatie}")

# def observaties_kaart(dag=None):
#     print()

# def seizoensanalyse(soort, jaar):
#     print()

# def biodiversiteit_analyse(maand=None, jaar=None):
#     print()