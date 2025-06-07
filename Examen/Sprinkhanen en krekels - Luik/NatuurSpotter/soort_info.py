# imports op basis van eigen kennis
import requests
from bs4 import BeautifulSoup
from datetime import date
import os
import csv
from fpdf import FPDF
from PIL import Image
# imports op basis van opzoekwerk op het internet
from io import BytesIO

def soort_info(soort):
    # BRON 1: Waarnemingen.be
    zoek_url = f"https://waarnemingen.be/search/?q={soort.replace(' ', '+')}"
    zoek_resp = requests.get(zoek_url)
    zoek_soup = BeautifulSoup(zoek_resp.text, "html.parser")
    lijstitem = zoek_soup.find("li", class_="lead")                
    a_tag = lijstitem.find("a", href=True)        
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
    latijnse_naam = latijn_tag.text.strip() if latijn_tag else "Onbekend"

    status_span = soup.find("span", class_="hidden-sm")
    status = status_span.text.strip() if status_span else "Onbekend"

    afbeelding_tag = soup.find("figure", class_="app-ratio-box-4-3 lightbox-gallery")
    if afbeelding_tag:
        img = afbeelding_tag.find("img")
        afbeelding_url = "https://waarnemingen.be" + img["src"] if img else "Geen afbeelding"
    else:
        afbeelding_url = "Geen afbeelding"

    # Haal waarnemingen op van het afgelopen jaar
    vandaag = date.today()
    vorig_jaar = vandaag.replace(year=vandaag.year - 1)
    obs_url = (f"https://waarnemingen.be/species/{soort_id}/observations/?date_after={vorig_jaar}&date_before={vandaag}&country_division=22")
    obs_resp = requests.get(obs_url)
    obs_soup = BeautifulSoup(obs_resp.text, "html.parser")
    tbody = obs_soup.find("tbody")
    
    observaties = []
    totaal_waarnemingen = 0
    laatste_waarneming = "Onbekend"
    maand_data = [0] * 12  # Voor seizoenspatroon
    
    if tbody:
        rijen = tbody.find_all("tr", class_=["even", "odd"])
        for rij in rijen[:50]:  # Meer data voor betere analyse
            kolommen = rij.find_all("td")
            if len(kolommen) >= 3:
                datum = kolommen[0].text.strip()
                aantal_raw = kolommen[1].get_text(separator=" ").strip()
                aantal = aantal_raw.split()[0]
                locatie = kolommen[2].text.strip()
                
                try:
                    aantal_int = int(aantal)
                    totaal_waarnemingen += aantal_int
                    
                    # Parse datum voor maandgegevens
                    if len(datum.split('-')) == 3:
                        maand = int(datum.split('-')[1]) - 1  # 0-indexed
                        if 0 <= maand < 12:
                            maand_data[maand] += aantal_int
                except ValueError:
                    pass
                
                if len(observaties) < 10:  # Bewaar top 10 voor display
                    observaties.append(f"{datum}   {aantal}   {locatie}")
        
        if observaties:
            laatste_waarneming = observaties[0].split()[0]

    # BRON 2: Wikipedia
    wiki_beschrijving = "Geen Wikipedia informatie gevonden"
    wiki_latijnse_naam = latijnse_naam

    wiki_zoek_url = f"https://nl.wikipedia.org/wiki/{soort.replace(' ', '_')}"
    wiki_resp = requests.get(wiki_zoek_url)
    wiki_soup = BeautifulSoup(wiki_resp.text, "html.parser")
    soort_cell = wiki_soup.find("td", class_="ta-center")

    if soort_cell:
        latijn_element = soort_cell.find("i")
        if latijn_element:
            wiki_latijnse_naam = latijn_element.find("b").text.strip() if latijn_element.find("b") else latijn_element.text.strip()
    
    content_div = wiki_soup.find("div", class_="mw-content-ltr mw-parser-output")
    if content_div:
        paragraphs = content_div.find_all("p")
        for p in paragraphs:
            text = p.get_text().strip()
            if len(text) > 100 and any(keyword in text.lower() for keyword in ['springhaan', 'familie', 'soort', 'kleur', 'lang']):
                wiki_beschrijving = text.replace('\n', ' ').strip()
                zinnen = wiki_beschrijving.split('. ')
                if len(zinnen) > 3:
                    wiki_beschrijving = '. '.join(zinnen[:3]) + '.'
                break

    volledige_beschrijving = ""
    if wiki_beschrijving != "Geen Wikipedia informatie gevonden":
        volledige_beschrijving = wiki_beschrijving
    if beschrijving != "Geen beschrijving gevonden" and beschrijving:
        if volledige_beschrijving:
            volledige_beschrijving += " " + beschrijving
        else:
            volledige_beschrijving = beschrijving
    
    if not volledige_beschrijving:
        volledige_beschrijving = f"Geen gedetailleerde beschrijving beschikbaar voor {soort}."

    # Maak data directory aan
    if not os.path.exists("data"):
        os.makedirs("data")

    # Soort data voor CSV
    soort_data = {
        'soort': soort,
        'scientific': wiki_latijnse_naam,
        'status': status,
        'observations': totaal_waarnemingen,
        'lastSeen': laatste_waarneming,
        'months': ','.join(map(str, maand_data)),  # Sla op als comma-separated string
        'description': volledige_beschrijving,
        'conservation': status,
        'image_url': afbeelding_url
    }

    # Schrijf naar CSV (append mode om meerdere soorten te verzamelen)
    csv_path = "data/soorten_info.csv"
    file_exists = os.path.isfile(csv_path)
    
    with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = soort_data.keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        writer.writerow(soort_data)

    print(f"Soortinformatie voor '{soort}' toegevoegd aan {csv_path}")

    # Maak ook nog steeds PDF aan
    maak_pdf(soort, soort_data, observaties, afbeelding_url)
    
    return soort_data

def maak_pdf(soort, soort_data, observaties, afbeelding_url):
    pad = f"data/{soort.replace(' ', '_')}.pdf"
    pdf = FPDF()
    pdf.add_page()

    # Titel
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(0, 8, soort, ln=True)

    # Afbeelding
    if afbeelding_url and afbeelding_url != "Geen afbeelding":
        img_data = requests.get(afbeelding_url).content
        img = Image.open(BytesIO(img_data))
        img_rgb = img.convert("RGB")
        img_path = "temp.jpg"
        img_rgb.save(img_path)
        pdf.image(img_path, x=10, y=pdf.get_y() + 3, w=70, h=50)
        os.remove(img_path)
        pdf.ln(60)

    # Informatie
    pdf.set_font("Helvetica", 'B', 11)
    pdf.cell(0, 6, f"Latijnse naam: {soort_data['scientific']}", ln=True)
    pdf.cell(0, 6, f"Zeldzaamheidsstatus: {soort_data['status']}", ln=True)
    pdf.ln(5)

    # Beschrijving
    pdf.set_font("Helvetica", 'B', 10)
    pdf.cell(0, 5, "Beschrijving:", ln=True)
    pdf.set_font("Helvetica", '', 9)
    pdf.multi_cell(0, 4, soort_data['description'])
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
            if len(parts) >= 3:
                if ":" in parts[1]:
                    datum = parts[0] + " " + parts[1]
                    aantal = parts[2]
                    locatie = " ".join(parts[3:])
                else:
                    datum = parts[0]
                    aantal = parts[1]
                    locatie = " ".join(parts[2:])
                pdf.cell(50, 4, datum, border=0)
                pdf.cell(20, 4, aantal, border=0)
                pdf.cell(0, 4, locatie, ln=True, border=0)
    else:
        pdf.ln(3)
        pdf.set_font("Helvetica", '', 8)
        pdf.cell(0, 6, "Geen waarnemingen gevonden", ln=True)

    # Voeg border toe rond de hele pagina
    pdf.set_line_width(0.3)
    margin = 5
    pdf.rect(x=margin, y=margin, w=pdf.w - 2*margin, h=pdf.h - 2*margin)

    pdf.output(pad)
    print(f"PDF opgeslagen als: {pad}")