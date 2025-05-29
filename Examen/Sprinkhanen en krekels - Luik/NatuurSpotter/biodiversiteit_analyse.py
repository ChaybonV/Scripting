# imports op basis van eigen kennis
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from fpdf import FPDF
import csv

def biodiversiteit_analyse(maand=None, jaar=None):
    nu = datetime.now()
    if maand is None:
        maand = nu.month
    elif isinstance(maand, str):
        maanden = {'januari':1, 'februari':2, 'maart':3, 'april':4, 'mei':5, 'juni':6, 'juli':7, 'augustus':8, 'september':9, 'oktober':10, 'november':11, 'december':12}
        maand = maanden.get(maand.lower(), nu.month)
    if jaar is None:
        jaar = nu.year
    else:
        jaar = int(jaar)

    url = (f"https://waarnemingen.be/species/?species_group_id=14&filter_month={maand}&filter_year={jaar}&filter_country_division=22&include_exotic_and_extinct=on")

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    type_s_div = soup.find("h2", id="type-S")
    table = type_s_div.find_next("table", class_="stupid-table")
    rows = table.find_all("tr")

    soorten_dict = {}
    totaal_waarnemingen = 0

    for row in rows[1:]:
        cols = row.find_all('td')
        if len(cols) < 7:
            continue
        
        soort_naam = cols[1].get_text(strip=True)
        wetenschappelijke_naam = cols[2].get_text(strip=True)
        aantal_waarnemingen = int(cols[5].get_text(strip=True).replace('.', ''))
        laatste_datum = cols[4].get_text(strip=True)

        key = f"{soort_naam} - {wetenschappelijke_naam}"
        soorten_dict[key] = {'aantal': aantal_waarnemingen,'laatste_waarneming': laatste_datum}
        totaal_waarnemingen += aantal_waarnemingen

    soortenrijkdom = len(soorten_dict)
    gemiddelde_per_soort = round(totaal_waarnemingen / soortenrijkdom, 2) if soortenrijkdom > 0 else 0
    maand_naam = datetime(jaar, maand, 1).strftime('%B')

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Titel
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(0, 10, f"Biodiversiteitsanalyse voor {maand_naam} {jaar}", ln=True)
    pdf.ln(5)

    # Samenvatting
    pdf.set_font("Helvetica", '', 12)
    pdf.cell(0, 8, f"Soortenrijkdom: {soortenrijkdom} unieke soorten", ln=True)
    pdf.cell(0, 8, f"Totaal aantal waarnemingen: {totaal_waarnemingen}", ln=True)
    pdf.cell(0, 8, f"Gemiddeld aantal waarnemingen per soort: {gemiddelde_per_soort}", ln=True)
    pdf.ln(8)

    # Tabel header
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(100, 8, "Soort", border=1)
    pdf.cell(35, 8, "Waarnemingen", border=1, align="C")
    pdf.cell(60, 8, "Laatste waarneming", border=1, align="C")
    pdf.ln()

    # Tabel data
    pdf.set_font("Helvetica", '', 11)
    for soort, data in soorten_dict.items():
        soort_tekst = soort
        max_len = 55
        if len(soort_tekst) > max_len:
            soort_tekst = soort_tekst[:max_len-3] + "..."
        pdf.cell(100, 7, soort_tekst, border=1)
        pdf.cell(35, 7, str(data['aantal']), border=1, align="C")
        pdf.cell(60, 7, data['laatste_waarneming'], border=1, align="C")
        pdf.ln()

    os.makedirs("data", exist_ok=True)
    pdf_pad = f"data/biodiversiteit_analyse_{maand}_{jaar}.pdf"
    pdf.output(pdf_pad)
    print(f"PDF-bestand opgeslagen in: {pdf_pad}")

    csv_bestand = f"data/waarnemingen_{maand}_{jaar}.csv"
    with open(csv_bestand, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['Soortnaam - Wetenschappelijke naam', 'Aantal waarnemingen', 'Laatste waarneming'])
        for soort, data in soorten_dict.items():
            writer.writerow([soort, data['aantal'], data['laatste_waarneming']])

    print(f"CSV-bestand opgeslagen in: {csv_bestand}")