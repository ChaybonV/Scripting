import requests
import threading
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser
import json

def daily_tarot(date):
    if isinstance(date, str):
        date = parser.parse(date)
    
    formatted_date = date.strftime('%Y-%m-%d')
    url = f"https://www.tarot.com/daily-tarot-card/{formatted_date}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    script = soup.find('script', type='application/ld+json')
    if not script:
        return "Could not find JSON data in the page."

    json_data = json.loads(script.string)
    article_body = json_data.get("articleBody", "")

    card_name_end = article_body.find(":")
    if card_name_end == -1:
        return "Could not find the end of the card name."

    card_name = article_body[:card_name_end].strip()
    card_name = ' '.join(card_name.split()[1:]).strip()
    card_description = article_body[card_name_end + 1:].strip()

    return {'card_name': card_name, 'card_description': card_description}

def moon_phase(date):
    if isinstance(date, str):
        date = parser.parse(date)

    timestamp = int(date.timestamp())
    url = f"https://api.farmsense.net/v1/moonphases/?d={timestamp}"
    response = requests.get(url)
    data = response.json()

    phase = data[0]["Phase"]
    illumination = round(data[0]["Illumination"] * 100)
    return {'phase': phase, 'illumination': f"{illumination}%"}

def solar_data(date, location):
    if isinstance(date, str):
        date = parser.parse(date)
    
    formatted_date = date.strftime('%Y-%m-%d')
    nominatim_url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json&limit=1"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(nominatim_url, headers=headers)
    data = response.json()
        
    lat = data[0]["lat"]
    lng = data[0]["lon"]

    solar_url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lng}&date={formatted_date}&formatted=1"
    solar_response = requests.get(solar_url)
    solar_data = solar_response.json()
    results = solar_data["results"]

    sunrise_time_obj = datetime.strptime(results['sunrise'], '%I:%M:%S %p')
    sunrise = sunrise_time_obj.strftime('%I:%M %p')

    sunset_time_obj = datetime.strptime(results['sunset'], '%I:%M:%S %p')
    sunset = sunset_time_obj.strftime('%I:%M %p')

    solar_noon_time_obj = datetime.strptime(results['solar_noon'], '%I:%M:%S %p')
    solar_noon = solar_noon_time_obj.strftime('%I:%M %p')

    h, m, s = map(int, results["day_length"].split(':'))
    day_length = f"{h} hours {m} minutes"

    return {'sunrise': sunrise, 'sunset': sunset, 'day_length': day_length, 'solar_noon': solar_noon}

def upcoming_events(date):
    if isinstance(date, str):
        date = parser.parse(date)

    year = date.year
    url = f"http://www.seasky.org/astronomy/astronomy-calendar-{year}.html"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    events_list = soup.find_all('li')
    events = []
    for event in events_list:
        date_span = event.find('span', class_='date-text')
        title_span = event.find('span', class_='title-text')
        p_tag = event.find('p')

        if date_span and title_span and p_tag:
            date_text = date_span.get_text(strip=True)
            title_text = title_span.get_text(strip=True)
            if ',' in date_text:
                date_parts = date_text.split(',')
                main_date = date_parts[0].strip()
                formatted_date = f"{main_date}, {year}"
            else:
                formatted_date = f"{date_text}, {year}"

            original_text = p_tag.get_text(strip=True)
            description = f"{date_text} - {title_text}"

            start_pos = original_text.find(title_text) + len(title_text)
            if start_pos > 0 and start_pos < len(original_text):
                rest_desc = original_text[start_pos:].strip()
                if rest_desc.startswith('.'):
                    rest_desc = rest_desc[1:].strip()
                description += f" {rest_desc}"

            events.append({'date': formatted_date, 'description': description.strip()})

    return events

def get_user_input():
    date_str = input()
    location = input()
    threading_choice = input().lower()
    multi_threaded = threading_choice == 'multi'
    
    date = parser.parse(date_str)
    return date, location, multi_threaded

def run_single_threaded(date, location):
    results = {}
    results['tarot'] = daily_tarot(date)
    results['moon'] = moon_phase(date)
    results['solar'] = solar_data(date, location)
    results['events'] = upcoming_events(date)
    return results

def run_multi_threaded(date, location):
    results = {}
    threads = []
    
    def run_tarot():
        results['tarot'] = daily_tarot(date)
    
    def run_moon():
        results['moon'] = moon_phase(date)
    
    def run_solar():
        results['solar'] = solar_data(date, location)
    
    def run_events():
        results['events'] = upcoming_events(date)
    
    threads.append(threading.Thread(target=run_tarot))
    threads.append(threading.Thread(target=run_moon))
    threads.append(threading.Thread(target=run_solar))
    threads.append(threading.Thread(target=run_events))
    
    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()
    
    return results

def write_to_file(date, results):
    formatted_date = date.strftime('%Y-%m-%d')
    filename = f"cosmic_data_{formatted_date}.txt"
    output_lines = []

    output_lines.append(date.strftime('%d/%m/%Y'))
    output_lines.append(results['solar'].get('location', ''))
    output_lines.append("multi" if results.get("multi_threaded") else "single")
    output_lines.append("")

    output_lines.append(f"Card name: {results['tarot']['card_name']}")
    output_lines.append(f"Card description: {results['tarot']['card_description']}")
    output_lines.append("")

    output_lines.append(f"Moon Phase: {results['moon']['phase']} ({results['moon']['illumination']} illuminated)")
    output_lines.append("")

    output_lines.append(f"Sunrise: {results['solar']['sunrise']}")
    output_lines.append(f"Sunset: {results['solar']['sunset']}")
    output_lines.append(f"Day Length: {results['solar']['day_length']}")
    output_lines.append(f"Solar Noon: {results['solar']['solar_noon']}")
    output_lines.append("")

    output_lines.append(f"Astronomical Events for {date.year}:")
    for event in results['events']:
        output_lines.append(f"- {event['date']}: {event['description']}")

    with open(filename, 'w') as f:
        for line in output_lines:
            print(line)
            f.write(line + "\n")

    print("\nSingle-threaded operation complete!" if not results.get("multi_threaded") else "Multi-threaded operation complete!")
    print(f"\nAll data saved to {filename}")

def main():
    date, location, multi_threaded = get_user_input()
    
    if multi_threaded:
        print("Running in multi-threaded mode...")
        results = run_multi_threaded(date, location)
    else:
        print("Running in single-threaded mode...")
        results = run_single_threaded(date, location)
    
    results['solar']['location'] = location
    results['multi_threaded'] = multi_threaded

    write_to_file(date, results)


if __name__ == "__main__":
    main()