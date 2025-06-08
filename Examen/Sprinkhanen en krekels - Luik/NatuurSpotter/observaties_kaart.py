"""
Functie om waarnemingen van dieren te visualiseren op een interactieve kaart.
Deze functie haalt data op van waarnemingen.be en toont deze op een folium kaart
met verschillende kleuren per soort.
"""

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
    """
    Genereert een interactieve kaart die waarnemingen visualiseert binnen de provincie.
    
    Parameters:
    dag (str): Optionele datum in YYYY-MM-DD formaat. 
               Als None, wordt de datum van vandaag gebruikt.
    """
    
    # Als er geen dag opgegeven wordt, gebruiken we vandaag
    if dag is None:
        dag = datetime.today().strftime('%Y-%m-%d')
    
    # URL samenstellen voor waarnemingen.be (soortgroep 14 = vogels, land 22 = België (Luik))
    url = f"https://waarnemingen.be/fieldwork/observations/daylist/?date={dag}&species_group=14&country_division=22"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Tabel met waarnemingen vinden
    table = soup.find("table", class_="table-bordered")
    rows = table.find("tbody").find_all("tr")
    
    # Geocoder instellen voor het omzetten van plaatsnamen naar coördinaten
    geolocator = Nominatim(user_agent="waarnemingen-scraper")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)  # Rate limiting om ban te voorkomen (per 1 seconde)
    
    # Kaart initialiseren (gecentreerd op België)
    kaart = folium.Map(location=[50.5, 5.5], zoom_start=9)
    
    kleuren = {} # Dictionary voor kleuren per soort
    data = [] # Lijst voor alle geldige data
    
    for rij in rows:
        kolommen = rij.find_all("td")
        
        # Overslaan als rij niet genoeg kolommen heeft
        if len(kolommen) < 5:
            continue
        
        # Soort en locatie info uit de HTML halen
        soort_html = kolommen[3]
        locatie_html = kolommen[4]
        
        # Tekst extraheren en opschonen
        soort_tekst = soort_html.text.strip()
        locatie_tekst = locatie_html.text.strip()
        
        # soms staat er extra info achter de soortnaam met een -
        if " - " in soort_tekst:
            soort_naam = soort_tekst.split(" - ")[0]
        else:
            soort_naam = soort_tekst
            
        # locatie naam schoonmaken - soms staan er haakjes achter
        if "(" in locatie_tekst:
            plaatsnaam = locatie_tekst.split("(")[0].strip()
        else:
            plaatsnaam = locatie_tekst
        
        # Coördinaten opzoeken voor de plaatsnaam
        locatie = geocode(f"{plaatsnaam}, Belgium")
        
        # Als de locatie gevonden is, voegen we het toe aan de data
        if locatie:
            lat, lon = locatie.latitude, locatie.longitude
            data.append((lat, lon, soort_naam, plaatsnaam))
    
    # Als er geen geldige locaties gevonden worden, stopt de code hier
    if not data:
        print("Geen locaties gevonden")
        return
    
    # Voor elke waarneming een marker toevoegen aan de kaart
    for lat, lon, soort, locatie_naam in data:
        # Nieuwe kleur toewijzen aan soort als nog niet bestaat (dit laten we random genereren)
        if soort not in kleuren:
            kleuren[soort] = "#{:06x}".format(random.randint(0, 0xFFFFFF))
        
        kleur = kleuren[soort]
        
        # HTML voor popup venster samenstellen
        html_popup = f'''
        <div style="min-width: 180px;">
            <b>Locatie:</b> {locatie_naam}<br>
            <b>Soort:</b> <span style="color: {kleur};">{soort}</span>
        </div>
        '''
        
        # Popup object maken
        popup = folium.Popup(folium.IFrame(html=html_popup, width=220, height=70), max_width=300)
        # Cirkelmarker toevoegen aan kaart met soort-specifieke kleur
        folium.CircleMarker(location=[lat, lon],radius=6,popup=popup,color=kleur,fill=True,fill_color=kleur,fill_opacity=0.9).add_to(kaart)
    
    # Legenda HTML samenstellen
    legenda_html = f'''
    <div style="position: fixed; bottom: 50px; left: 50px; background-color: white; border: 1px solid gray; padding: 10px; max-height: 200px; overflow-y: auto; font-family: Arial, sans-serif; font-size: 12px; z-index: 9999;">
        <b>Soorten op {datetime.strptime(dag, '%Y-%m-%d').strftime('%d-%m-%Y')}</b><br>
    '''
    
    # Voor elke soort een regel in de legende toevoegen
    for soort, kleur in kleuren.items():
        legenda_html += f'''
        <div style="margin: 4px 0; display: flex; align-items: center;">
            <span style="background-color: {kleur}; display: inline-block; width: 15px; height: 15px; margin-right: 8px; border: 1px solid #555;"></span>
            {soort}
        </div>
        '''
    legenda_html += '</div>'
    
    # Legende toevoegen aan kaart
    kaart.get_root().html.add_child(folium.Element(legenda_html))
    
    # Data map aanmaken als deze niet bestaat
    os.makedirs("data", exist_ok=True)
    
    # Kaart opslaan met datum als bestandsnaam
    kaart_path = os.path.join("data", f"{datetime.strptime(dag, '%Y-%m-%d').strftime('%d-%m-%Y')}.html")
    kaart.save(kaart_path)
    print(f"Kaart opgeslagen als {kaart_path}")