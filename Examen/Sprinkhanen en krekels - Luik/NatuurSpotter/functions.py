import os
import requests
from bs4 import BeautifulSoup
from datetime import date, datetime
from fpdf import FPDF
from PIL import Image
from io import BytesIO
import folium
import random
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import matplotlib.pyplot as plt


def soort_info(soort):
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

    if not os.path.exists("data"):
        os.makedirs("data")

    pad = f"data/{soort.replace(' ', '_')}.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Titel
    pdf.set_font("Helvetica", 'B', 18)
    pdf.cell(0, 10, soort, ln=True)

    # Afbeelding
    if afbeelding_url:
        img_data = requests.get(afbeelding_url).content
        img = Image.open(BytesIO(img_data))
        img_rgb = img.convert("RGB")
        img_path = "temp.jpg"
        img_rgb.save(img_path)
        pdf.image(img_path, x=10, y=pdf.get_y() + 5, w=80, h=60)
        os.remove(img_path)
        pdf.ln(65)

    # Latijnse naam en status
    pdf.set_font("Helvetica", 'B', 11)
    pdf.cell(0, 8, f"Latijnse naam: {latijnse_naam}", ln=True)
    pdf.cell(0, 8, f"Zeldzaamheidstatus: {status}", ln=True)
    pdf.ln(5)

    # Beschrijving
    pdf.set_font("Helvetica", '', 9)
    beschrijving_regels = beschrijving.split("\n")
    for regel in beschrijving_regels:
        pdf.multi_cell(0, 5, regel)
    pdf.ln(5)

    # Observaties
    if observaties:
        pdf.set_font("Helvetica", 'B', 10)
        pdf.cell(50, 7, "Datum", border=0)
        pdf.cell(20, 7, "Aantal", border=0)
        pdf.cell(0, 7, "Locatie", ln=True, border=0)

        pdf.set_font("Helvetica", '', 9)
        for lijn in observaties:
            parts = lijn.split()
            if len(parts) >= 4:
                datum = parts[0] + " " + parts[1]
                aantal = parts[2]
                locatie = " ".join(parts[3:])
                pdf.cell(50, 6, datum, border=0)
                pdf.cell(20, 6, aantal, border=0)
                pdf.cell(0, 6, locatie, ln=True, border=0)
            else:
                pdf.cell(0, 6, lijn, ln=True)
    else:
        pdf.ln(5)
        pdf.set_font("Helvetica", '', 9)
        pdf.cell(0, 8, "Geen waarnemingen gevonden", ln=True)

    pdf.set_line_width(0.3)
    margin = 5
    pdf.rect(x=margin, y=margin, w=pdf.w - 2*margin, h=pdf.h - 2*margin)

    pdf.output(pad)
    print(f"PDF opgeslagen als: {pad}")

def observaties_kaart(dag=None):
    if dag is None:
        dag = datetime.today().strftime('%Y-%m-%d')

    url = f"https://waarnemingen.be/fieldwork/observations/daylist/?date={dag}&species_group=14&country_division=22"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", class_="table-bordered")
    rows = table.find("tbody").find_all("tr")

    geolocator = Nominatim(user_agent="waarnemingen-scraper")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    kaart = folium.Map(location=[50.5, 5.5], zoom_start=9)

    kleuren = {}
    data = []

    for rij in rows:
        kolommen = rij.find_all("td")
        if len(kolommen) < 5:
            continue

        soort_html = kolommen[3]
        locatie_html = kolommen[4]

        soort_naam = soort_html.text.strip().split(" - ")[0]
        locatie_naam = locatie_html.text.strip()
        plaatsnaam = locatie_naam.split("(")[0].strip()
        locatie = geocode(f"{plaatsnaam}, Belgium")

        if locatie:
            lat, lon = locatie.latitude, locatie.longitude
            data.append((lat, lon, soort_naam, plaatsnaam))

    if not data:
        print("Geen locaties gevonden")
        return

    for lat, lon, soort, locatie in data:
        if soort not in kleuren:
            kleuren[soort] = "#{:06x}".format(random.randint(0, 0xFFFFFF))
        kleur = kleuren[soort]

        html_popup = f'''
        <div style="min-width: 180px;">
            <b>Locatie:</b> {plaatsnaam}<br>
            <b>Soort:</b> <span style="color: {kleur};">{soort}</span>
        </div>
        '''

        popup = folium.Popup(folium.IFrame(html=html_popup, width=220, height=70), max_width=300)
        folium.CircleMarker(location=[lat, lon],radius=6,popup=popup,color=kleur,fill=True,fill_color=kleur,fill_opacity=0.9).add_to(kaart)

    legenda_html = f'''
    <div style="position: fixed; bottom: 50px; left: 50px; background-color: white; border: 1px solid gray; padding: 10px; max-height: 200px; overflow-y: auto; font-family: Arial, sans-serif; font-size: 12px; z-index: 9999;">
        <b>Soorten op {datetime.strptime(dag, '%Y-%m-%d').strftime('%d-%m-%Y')}</b><br>
    '''
    for soort, kleur in kleuren.items():
        legenda_html += f'''
        <div style="margin: 4px 0; display: flex; align-items: center;">
            <span style="background-color: {kleur}; display: inline-block; width: 15px; height: 15px; margin-right: 8px; border: 1px solid #555;"></span>
            {soort}
        </div>
        '''
    legenda_html += '</div>'

    kaart.get_root().html.add_child(folium.Element(legenda_html))
    os.makedirs("data", exist_ok=True)
    kaart_path = os.path.join("data", f"{datetime.strptime(dag, '%Y-%m-%d').strftime('%d-%m-%Y')}.html")
    kaart.save(kaart_path)
    print(f"Kaart opgeslagen als {kaart_path}")

def seizoensanalyse(soort, jaar):
    zoek_url = f"https://waarnemingen.be/search/?q={soort.replace(' ', '+')}"
    zoek_resp = requests.get(zoek_url)
    zoek_soup = BeautifulSoup(zoek_resp.text, "html.parser")

    lijstitem = zoek_soup.find("li", class_="lead")
    href = lijstitem.find("a")["href"]
    soort_id = href.strip("/").split("/")[-1]

    telling = {"Lente": 0, "Zomer": 0, "Herfst": 0, "Winter": 0}

    base_url = f"https://waarnemingen.be/species/{soort_id}/observations/?date_after={jaar}-01-01&date_before={jaar}-12-31&country_division=22"
    eerste_resp = requests.get(base_url)
    eerste_soup = BeautifulSoup(eerste_resp.text, "html.parser")
    pagination = eerste_soup.find("ul", class_="pagination")

    if pagination:
        page_links = pagination.find_all("a")
        page_numbers = [int(a.text) for a in page_links if a.text.isdigit()]
        max_page = max(page_numbers) if page_numbers else 1
    else:
        max_page = 1

    def verwerk_pagina(html):
        soup = BeautifulSoup(html, "html.parser")
        tbody = soup.find("tbody")
        if not tbody:
            return

        for rij in tbody.find_all("tr", class_=["even", "odd"]):
            kolommen = rij.find_all("td")
            if not kolommen:
                continue

            datum = datetime.strptime(kolommen[0].text.strip().split()[0], "%Y-%m-%d").date()
            dag = datum.day
            maand = datum.month

            if (maand == 3 and dag >= 21) or maand in [4, 5] or (maand == 6 and dag <= 20):
                telling["Lente"] += 1
            elif (maand == 6 and dag >= 21) or maand in [7, 8] or (maand == 9 and dag <= 22):
                telling["Zomer"] += 1
            elif (maand == 9 and dag >= 23) or maand in [10, 11] or (maand == 12 and dag <= 20):
                telling["Herfst"] += 1
            else:
                telling["Winter"] += 1

    verwerk_pagina(eerste_resp.text)
    for pagina in range(2, max_page + 1):
        url = base_url + f"&page={pagina}"
        resp = requests.get(url)
        verwerk_pagina(resp.text)

    labels = list(telling.keys())
    values = list(telling.values())

    plt.figure(figsize=(8,5))
    plt.bar(labels, values, color=["lightgreen", "orange", "sienna", "skyblue"])
    plt.title(f'Waarnemingen van "{soort}" per seizoen in {jaar}')
    plt.xlabel("Seizoen")
    plt.ylabel("Aantal waarnemingen")
    plt.tight_layout()

    os.makedirs("data", exist_ok=True)
    plot_path = f"data/{soort.replace(' ', '_')}_{jaar}_seizoensanalyse.png"
    plt.savefig(plot_path)
    plt.close()

    minst_voorkomend_seizoen = min(telling, key=telling.get)
    meest_voorkomend_seizoen = max(telling, key=telling.get)

    prompt = (
        f"Voor de soort '{soort}' zijn er in het jaar {jaar} minder waarnemingen in de {minst_voorkomend_seizoen.lower()}."
        f" Waarom zou deze soort dan minder worden waargenomen in de {minst_voorkomend_seizoen.lower()} en hoe komt het dat ze vaker zichtbaar zijn in de {meest_voorkomend_seizoen.lower()}? Benoem dit in een tekst van ongeveer 10 zinnen."
    )

    llm_payload = {
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "web_access": False
    }

    headers = {
        "x-rapidapi-key": "a69cdae89amshdb1eb1b1b44f30bp1f4e96jsn8f47560ad780",
        "x-rapidapi-host": "open-ai21.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    response = requests.post("https://open-ai21.p.rapidapi.com/conversationllama", json=llm_payload, headers=headers)
    result = response.json()
    uitleg = result["result"]

    pdf_path = f"data/{soort.replace(' ', '_')}_{jaar}_seizoensanalyse.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Voeg plot afbeelding toe
    pdf.image(plot_path, x=10, y=10, w=pdf.w - 20)
    pdf.ln(130)

    # Voeg uitleg toe
    pdf.set_font("Helvetica", '', 11)
    uitleg_regels = uitleg.split('\n')
    for regel in uitleg_regels:
        pdf.multi_cell(0, 8, regel)
    pdf.output(pdf_path)

    print(f"PDF opgeslagen als: {pdf_path}")

# def biodiversiteit_analyse(maand=None, jaar=None):
#     print()