# imports op basis van eigen kennis
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from fpdf import FPDF
import matplotlib.pyplot as plt

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