# imports op basis van eigen kennis
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import random
# imports op basis van opzoekwerk op het internet
import folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

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
    
    for lat, lon, soort, locatie_naam in data:
        if soort not in kleuren:
            kleuren[soort] = "#{:06x}".format(random.randint(0, 0xFFFFFF))
        kleur = kleuren[soort]
        
        html_popup = f'''
        <div style="min-width: 180px;">
            <b>Locatie:</b> {locatie_naam}<br>
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