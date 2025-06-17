"""
Functie om biodiversiteitsgegevens per maand te analyseren en rapporteren.
Deze functie haalt soortgegevens op van waarnemingen.be, berekent biodiversiteitsstatistieken
en genereert zowel een PDF-rapport als een CSV-bestand voor verdere verwerking.
"""

# imports op basis van eigen kennis
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from fpdf import FPDF
import csv

def biodiversiteit_analyse(maand=None, jaar=None):
    """
    Analyseert biodiversiteitsgegevens voor een specifieke maand en jaar.
    Berekent statistieken zoals soortenrijkdom en waarnemingsfrequentie.
    Genereert een PDF-rapport en CSV-bestand met de resultaten.
    
    Parameters:
    maand (int/str): Maandnummer (1-12) of maandnaam. Als None, wordt huidige maand gebruikt.
    jaar (int): Jaar voor analyse. Als None, wordt huidig jaar gebruikt.
    """
    
    # Maand parameter verwerken
    if maand is None:
        maand = datetime.now().month  # Gebruik huidige maand als geen maand opgegeven

    if type(maand) == str:
        maanden = {'januari': 1, 'februari': 2, 'maart': 3, 'april': 4, 'mei': 5, 'juni': 6, 'juli': 7, 'augustus': 8, 'september': 9, 'oktober': 10, 'november': 11, 'december': 12}
        if maand.lower() in maanden:
            maand = maanden[maand.lower()]
        else:
            maand = datetime.now().month
    
    # Jaar parameter verwerken
    if jaar is None:
        jaar = datetime.now().year  # Gebruik huidig jaar als geen jaar opgegeven
    else:
        jaar = int(jaar)

    # URL samenstellen voor waarnemingen.be (soortgroep 14 = Sprinkhanen en Krekels, land 22 = België (Luik))
    url = f"https://waarnemingen.be/species/?species_group_id=14&filter_month={maand}&filter_year={jaar}&filter_country_division=22&include_exotic_and_extinct=on"

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Specifieke sectie vinden met soortgegevens (type-S = Species)
    type_s_div = soup.find("h2", id="type-S")
    table = type_s_div.find_next("table", class_="stupid-table")
    rows = table.find_all("tr")

    # Dictionary voor het opslaan van soortgegevens
    soorten_dict = {}
    totaal_waarnemingen = 0

    # Door alle tabelrijen gaaan (eerste rij overslaan = header)
    for row in rows[1:]:
        cols = row.find_all('td')
        
        # Overslaan als rij niet genoeg kolommen heeft
        if len(cols) < 7:
            continue
        
        # Gegevens uit kolommen halen
        soort_naam = cols[1].get_text(strip=True)
        wetenschappelijke_naam = cols[2].get_text(strip=True)
        aantal_waarnemingen = int(cols[5].get_text(strip=True).replace('.', ''))
        laatste_datum = cols[4].get_text(strip=True)

        # Unieke sleutel maken door beide namen te combineren
        key = f"{soort_naam} - {wetenschappelijke_naam}"
        soorten_dict[key] = {'aantal': aantal_waarnemingen,'laatste_waarneming': laatste_datum}
        totaal_waarnemingen += aantal_waarnemingen

    # Biodiversiteitsstatistieken berekenen
    soortenrijkdom = len(soorten_dict)  # Aantal unieke soorten
    gemiddelde_per_soort = round(totaal_waarnemingen / soortenrijkdom, 2) if soortenrijkdom > 0 else 0
    maand_naam = datetime(jaar, maand, 1).strftime('%B')  # Volledige maandnaam

    # PDF-rapport genereren
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Hoofdtitel
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(0, 10, f"Biodiversiteitsanalyse voor {maand_naam} {jaar}", ln=True)
    pdf.ln(5)

    # Samenvattingsstatistieken
    pdf.set_font("Helvetica", '', 12)
    pdf.cell(0, 8, f"Soortenrijkdom: {soortenrijkdom} unieke soorten", ln=True)
    pdf.cell(0, 8, f"Totaal aantal waarnemingen: {totaal_waarnemingen}", ln=True)
    pdf.cell(0, 8, f"Gemiddeld aantal waarnemingen per soort: {gemiddelde_per_soort}", ln=True)
    pdf.ln(8)

    # Tabelheader voor soortgegevens
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(100, 8, "Soort", border=1)
    pdf.cell(35, 8, "Waarnemingen", border=1, align="C")
    pdf.cell(60, 8, "Laatste waarneming", border=1, align="C")
    pdf.ln()

    # Tabeldata: alle soorten met hun gegevens
    pdf.set_font("Helvetica", '', 11)
    for soort, data in soorten_dict.items():
        # Lange soortnamen inkorten om in tabel te passen
        soort_tekst = soort
        max_len = 55
        if len(soort_tekst) > max_len:
            soort_tekst = soort_tekst[:max_len-3] + "..."
        
        # Tabelrij toevoegen
        pdf.cell(100, 7, soort_tekst, border=1)
        pdf.cell(35, 7, str(data['aantal']), border=1, align="C")
        pdf.cell(60, 7, data['laatste_waarneming'], border=1, align="C")
        pdf.ln()

    # Data map aanmaken en PDF opslaan
    os.makedirs("data", exist_ok=True)
    pdf_pad = f"data/biodiversiteit_analyse_{maand}_{jaar}.pdf"
    pdf.output(pdf_pad)
    print(f"PDF-bestand opgeslagen in: {pdf_pad}")

    # CSV-bestand genereren voor verdere verwerking (hebben we nodig in node-red)
    csv_bestand = f"data/waarnemingen_{maand}_{jaar}.csv"
    with open(csv_bestand, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')  # Puntkomma als separator
        
        # CSV header
        writer.writerow(['Soortnaam - Wetenschappelijke naam', 'Aantal waarnemingen', 'Laatste waarneming'])
        
        # Alle soortgegevens naar CSV schrijven
        for soort, data in soorten_dict.items():
            writer.writerow([soort, data['aantal'], data['laatste_waarneming']])

    print(f"CSV-bestand opgeslagen in: {csv_bestand}")