# imports op basis van eigen kennis
import requests
from bs4 import BeautifulSoup
from datetime import date
import os
from fpdf import FPDF
from PIL import Image
# imports op basis van opzoekwerk op het internet
from io import BytesIO

def soort_info(soort):
    # BRON 1
    zoek_url = f"https://waarnemingen.be/search/?q={soort.replace(' ', '+')}"
    zoek_resp = requests.get(zoek_url)
    zoek_soup = BeautifulSoup(zoek_resp.text, "html.parser")

    lijstitem = zoek_soup.find("li", class_="lead")
    if not lijstitem:
        print(f"Geen resultaten gevonden voor '{soort}' op waarnemingen.be")
        return
        
    a_tag = lijstitem.find("a", href=True)
    if not a_tag:
        print(f"Geen link gevonden voor '{soort}' op waarnemingen.be")
        return
        
    href = a_tag["href"]
    soort_id = href.strip("/").split("/")[-1]
    soort_url = f"https://waarnemingen.be{href}"
    resp = requests.get(soort_url)
    soup = BeautifulSoup(resp.text, "html.parser")
    soortgroep_link = soup.find("a", href="/species/search/?species_group=14")

    if not soortgroep_link:
        print("Deze soort behoort niet tot de soortgroep 'Sprinkhanen en krekels'")
        return

    beschrijving_div = soup.find("div", class_="app-content-section js-user-content")
    beschrijving = beschrijving_div.get_text().strip() if beschrijving_div else "Geen beschrijving gevonden"

    latijn_tag = soup.find("i", class_="species-scientific-name")
    latijnse_naam = latijn_tag.text.strip() if latijn_tag else "Geen latijnse naam gevonden"

    status_span = soup.find("span", class_="hidden-sm")
    status = status_span.text.strip() if status_span else "Geen zeldzaamheidsstatus gevonden"

    afbeelding_tag = soup.find("figure", class_="app-ratio-box-4-3 lightbox-gallery")
    img = afbeelding_tag.find("img") if afbeelding_tag else None
    afbeelding_url = "https://waarnemingen.be" + img["src"] if img else "Geen afbeelding gevonden"

    vandaag = date.today()
    vorig_jaar = vandaag.replace(year=vandaag.year - 1)
    obs_url = (f"https://waarnemingen.be/species/{soort_id}/observations/"f"?date_after={vorig_jaar}&date_before={vandaag}&country_division=22")
    obs_resp = requests.get(obs_url)
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
                aantal = aantal_raw.split()[0] if aantal_raw else "Geen aantal gevonden"
                locatie = kolommen[2].text.strip()
                observaties.append(f"{datum}   {aantal}   {locatie}")

    # BRON 2
    wiki_beschrijving = "Geen Wikipedia informatie gevonden"
    wiki_latijnse_naam = latijnse_naam

    wiki_zoek_url = f"https://nl.wikipedia.org/wiki/{soort.replace(' ', '_')}"
    wiki_resp = requests.get(wiki_zoek_url)
    
    if wiki_resp.status_code == 200:
        wiki_soup = BeautifulSoup(wiki_resp.text, "html.parser")
        
        soort_cell = wiki_soup.find("td", class_="ta-center")
        if soort_cell:
            latijn_element = soort_cell.find("i")
            if latijn_element:
                wiki_latijnse_naam = latijn_element.find("b").text.strip() if latijn_element.find("b") else latijn_element.text.strip()
        
        # Haal nuttige paragraaf van Wikipedia
        content_div = wiki_soup.find("div", class_="mw-content-ltr mw-parser-output")
        if content_div:
            paragraphs = content_div.find_all("p")
            for p in paragraphs:
                text = p.get_text().strip()
                # Neem alleen relevante paragrafen (niet navigatie)
                if len(text) > 100 and any(keyword in text.lower() for keyword in ['insect', 'springhaan', 'familie', 'soort', 'kleur', 'lang']):
                    wiki_beschrijving = text.replace('\n', ' ').strip()
                    # Beperk tot eerste 2-3 zinnen voor beknoptheid
                    zinnen = wiki_beschrijving.split('. ')
                    if len(zinnen) > 3:
                        wiki_beschrijving = '. '.join(zinnen[:3]) + '.'
                    break

    if not os.path.exists("data"):
        os.makedirs("data")

    pad = f"data/{soort.replace(' ', '_')}.pdf"
    pdf = FPDF()
    pdf.add_page()

    # Titel
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(0, 8, soort, ln=True)

    # Afbeelding
    if afbeelding_url and afbeelding_url != "Geen afbeelding gevonden":
        img_data = requests.get(afbeelding_url).content
        img = Image.open(BytesIO(img_data))
        img_rgb = img.convert("RGB")
        img_path = "temp.jpg"
        img_rgb.save(img_path)
        pdf.image(img_path, x=10, y=pdf.get_y() + 3, w=70, h=50)
        os.remove(img_path)
        pdf.ln(60)

    # Latijnse naam
    pdf.set_font("Helvetica", 'B', 11)
    pdf.cell(0, 6, f"Latijnse naam: {wiki_latijnse_naam}", ln=True)
    pdf.cell(0, 6, f"Zeldzaamheidsstatus: {status}", ln=True)
    pdf.ln(5)

    # Beschrijving
    pdf.set_font("Helvetica", '', 9)
    # Wikipedia beschrijving
    if wiki_beschrijving != "Geen Wikipedia informatie gevonden":
        pdf.set_font("Helvetica", 'B', 10)
        pdf.cell(0, 5, "Algemene beschrijving:", ln=True)
        pdf.set_font("Helvetica", '', 9)
        wiki_regels = wiki_beschrijving.split("\n")
        for regel in wiki_regels:
            if regel.strip():
                pdf.multi_cell(0, 4, regel.strip())
        pdf.ln(2)
    # Waarnemingen.be beschrijving 
    if beschrijving != "Geen beschrijving gevonden":
        pdf.set_font("Helvetica", 'B', 10)
        pdf.cell(0, 5, "Aanvullende informatie:", ln=True)
        pdf.set_font("Helvetica", '', 9)
        beschrijving_regels = beschrijving.split("\n")
        for regel in beschrijving_regels:
            if regel.strip():
                pdf.multi_cell(0, 4, regel.strip())
    pdf.ln(5)

    # Observaties
    if observaties:
        pdf.set_font("Helvetica", 'B', 10)
        pdf.cell(50, 5, "Datum", border=0)
        pdf.cell(20, 5, "Aantal", border=0)
        pdf.cell(0, 5, "Locatie", ln=True, border=0)

        pdf.set_font("Helvetica", '', 8)
        for lijn in observaties:
            parts = lijn.split()
            if len(parts) >= 4:
                # Check of het 2e deel een tijd is (bevat ":")
                if ":" in parts[1]:
                    # Datum + tijd format
                    datum = parts[0] + " " + parts[1]
                    aantal = parts[2]
                    locatie = " ".join(parts[3:])
                else:
                    # Alleen datum format (geen tijd)
                    datum = parts[0]
                    aantal = parts[1]
                    locatie = " ".join(parts[2:])
                pdf.cell(50, 4, datum, border=0)
                pdf.cell(20, 4, aantal, border=0)
                pdf.cell(0, 4, locatie, ln=True, border=0)
            else:
                pdf.cell(0, 4, lijn, ln=True)
    else:
        pdf.ln(3)
        pdf.set_font("Helvetica", '', 8)
        pdf.cell(0, 6, "Geen waarnemingen gevonden", ln=True)

    pdf.set_line_width(0.3)
    margin = 5
    pdf.rect(x=margin, y=margin, w=pdf.w - 2*margin, h=pdf.h - 2*margin)

    pdf.output(pad)
    print(f"PDF opgeslagen als: {pad}")