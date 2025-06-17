# NatuurSpotter 🦗

Een Python package voor het analyseren en visualiseren van natuurwaarnemingen in de provincie Luik, België. Deze tool haalt data op van waarnemingen.be en Wikipedia om uitgebreide rapporten en visualisaties te genereren.
Dit project is gemaakt voor het vak Scripting binnen de opleiding Applied Data Intelligence aan Thomas More Mechelen.

## 📋 Overzicht

NatuurSpotter biedt vier hoofdfuncties voor natuuronderzoek:

- **Soortinformatie**: Gedetailleerde rapporten over specifieke diersoorten
- **Interactieve observatie kaarten**: Visualisatie van waarnemingen op een bepaalde dag
- **Seizoensanalyse**: Patronen in waarnemingen doorheen het jaar
- **Biodiversiteitsanalyse**: Soortenrijkdom per maand

## 🛠️ Installatie

### Vereiste Python packages:
```bash
pip install requests beautifulsoup4 fpdf2 pillow matplotlib folium geopy
```

### Project structuur:
```
NatuurSpotter/
├── init.py
├── soort_info.py
├── observaties_kaart.py
├── seizoensanalyse.py
├── biodiversiteit_analyse.py
data/
├── Opslagplaats voor automatisch aangemaakte bestanden (csv, pdf, html)
node-red/
├── node_red_flow.json
├── Afbeeldingen van dashboard
demo.ipynb
LICENSE
README.md
```

## 🚀 Gebruik

### Import van de modules:
```python
from NatuurSpotter import soort_info, observaties_kaart, seizoensanalyse, biodiversiteit_analyse
```

## 📖 Functies

### 1. Soortinformatie (`soort_info`)

Genereert een uitgebreid rapport over een specifieke diersoort met informatie van waarnemingen.be en Wikipedia.

```python
soort_info.soort_info("Wrattenbijter")
```

**Parameters:**
- `soort`: Naam van een bestaande Sprinkhaan of Krekel

**Output:**
- PDF-rapport met soortbeschrijving, foto en waarnemingstabel
- CSV-bestand met gestructureerde data voor Node-RED

**Bevat:**
- Latijnse naam en zeldzaamheidsstatus
- Beschrijving vanuit Wikipedia en waarnemingen.be
- Afbeelding van de soort
- Recente waarnemingen (laatste 10)
- Totaal aantal waarnemingen afgelopen jaar

---

### 2. Observaties Kaart (`observaties_kaart`)

Creëert een interactieve kaart met alle waarnemingen van een specifieke dag.

```python
observaties_kaart.observaties_kaart("2025-05-25")
```

**Parameters:**
- `dag` (optioneel): Datum in YYYY-MM-DD formaat. Standaard = vandaag

**Output:**
- HTML-bestand met interactieve Folium kaart
- Kleurgecodeerde markers per soort
- Popup informatie bij elke waarneming
- Legenda met alle waargenomen soorten

---

### 3. Seizoensanalyse (`seizoensanalyse`)

Analyseert waarnemingspatronen per seizoen en genereert een verklaring via AI.

```python
seizoensanalyse.seizoensanalyse("Veldkrekel", 2022)
```

**Parameters:**
- `soort`: Naam van de diersoort
- `jaar`: Jaar voor analyse

**Output:**
- PNG-grafiek met seizoensverdeling
- PDF-rapport met grafiek en AI-gegenereerde verklaring
- Gebruikt externe LLM API voor biologische uitleg

**Seizoensdefinities:**
- **Lente**: 21 maart - 20 juni
- **Zomer**: 21 juni - 22 september  
- **Herfst**: 23 september - 20 december
- **Winter**: 21 december - 20 maart

---

### 4. Biodiversiteitsanalyse (`biodiversiteit_analyse`)

Berekent biodiversiteitsstatistieken voor een specifieke maand.

```python
biodiversiteit_analyse.biodiversiteit_analyse("april", 2024)
```

**Parameters:**
- `maand` (optioneel): Maandnummer (1-12) of maandnaam. Standaard = huidige maand
- `jaar` (optioneel): Jaar voor analyse. Standaard = huidig jaar

**Output:**
- PDF-rapport met soortenlijst en statistieken
- CSV-bestand voor verdere verwerking in Node-RED

**Statistieken:**
- Soortenrijkdom (aantal unieke soorten)
- Totaal aantal waarnemingen
- Gemiddeld aantal waarnemingen per soort
- Laatste waarneming per soort

## 📁 Output Bestanden

Alle gegenereerde bestanden worden opgeslagen in de `data/` map (voorbeeld):

```
data/
├── Wrattenbijter.pdf                              # Soortrapport
├── soorten_info.csv                               # CSV voor Node-RED
├── 25-05-2025.html                               # Interactieve kaart
├── Veldkrekel_2022_seizoensanalyse.png          # Seizoensgrafiek
├── Veldkrekel_2022_seizoensanalyse.pdf          # Seizoensrapport
├── biodiversiteit_analyse_4_2024.pdf            # Biodiversiteitsrapport
└── waarnemingen_4_2024.csv                      # Biodiversiteitsdata
```

## 🌐 Databronnen

- **waarnemingen.be**: Waarnemingsdata, soortinformatie, afbeeldingen
- **Wikipedia**: Wetenschappelijke beschrijvingen
- **OpenAI API**: AI-gegenereerde verklaringen (seizoensanalyse)

## ⚙️ Technische Details

### Afhankelijkheden:
- `requests`: HTTP requests naar websites
- `beautifulsoup4`: HTML parsing
- `fpdf2`: PDF generatie
- `pillow`: Beeldverwerking
- `matplotlib`: Grafiekgeneratie
- `folium`: Interactieve kaarten
- `geopy`: Geocoding van plaatsnamen

### Beperkingen:
- Focust op provincie 22 (Luik)
- Focust op Soortgroep 14 (Sprinkhanen en Krekels)
- Rate limiting voor geocoding (1 request/seconde)
- Vereist internet verbinding

## 🔧 API Configuratie

Voor seizoensanalyse is een RapidAPI key vereist:
```python
headers = {
    "x-rapidapi-key": "YOUR_API_KEY_HERE",
    "x-rapidapi-host": "open-ai21.p.rapidapi.com"
}
```

## 📊 Node-RED Integratie

De gegenereerde CSV-bestanden zijn geoptimaliseerd voor gebruik in Node-RED:
- Alle velden zijn gequote voor betrouwbare parsing
- Puntkomma als separator

## ⚠️ Gebruiksvoorwaarden

Let op de gebruiksvoorwaarden van:
- waarnemingen.be
- Wikipedia
- External API providers

Respecteer rate limits en gebruik de tool verantwoordelijk voor onderzoeks- en educatieve doeleinden. Andere doeleinden zijn zeker mogelijk.