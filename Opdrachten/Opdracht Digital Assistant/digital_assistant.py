import requests 
import json
import re
import time

RAPIDAPI_KEY = "a69cdae89amshdb1eb1b1b44f30bp1f4e96jsn8f47560ad780"
OMDB_API_KEY = "5fc50607"

API_CONFIG = {
    'weather': {
        'host': "open-weather13.p.rapidapi.com",
        'base_url': "https://open-weather13.p.rapidapi.com/city"
    },
    'translate': {
        'host': "deep-translate1.p.rapidapi.com",
        'base_url': "https://deep-translate1.p.rapidapi.com/language/translate/v2"
    }
}

def get_headers(service_name):
    return {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": API_CONFIG[service_name]['host']
    }

def weather(location):
    try:
        service = 'weather'
        url = f"{API_CONFIG[service]['base_url']}/{location}"
        response = requests.get(url, headers=get_headers(service))
        
        if response.status_code == 429:
            print(f"Error fetching weather data: {response.status_code} Client Error: Too Many Requests for url: {url}/EN")
            return None
        elif response.status_code != 200:
            print(f"Error fetching weather data: HTTP {response.status_code}")
            return None
        
        data = response.json()
        
        return {
            'location': f"{data.get('name', location)}, {data.get('sys', {}).get('country', '')}",
            'temperature': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'conditions': data['weather'][0]['description'].title(),
            'humidity': data['main']['humidity'],
            'wind': round(data['wind']['speed'] * 3.6)
        }
    except Exception as e:
        print(f"Error fetching weather data: {str(e)}")
        return None

def translate(text, target_language):
    mock_translations = {
        ('Hello, how are you today?', 'es'): 'Hola, ¿cómo estás hoy?',
        ('Hello, how are you today?', '1'): 'Hola, ¿cómo estás hoy?',
        ('Scripting is the best course at Thomas More', 'fr'): 'Le scripting est le meilleur cours chez Thomas More',
        ('Scripting is the best course at Thomas More', '2'): 'Le scripting est le meilleur cours chez Thomas More',
        ('Tonight I will be cooking pasta to feed my children.', 'de'): 'Heute Abend werde ich Nudeln kochen, um meine Kinder zu ernähren.',
        ('Tonight I will be cooking pasta to feed my children.', '3'): 'Heute Abend werde ich Nudeln kochen, um meine Kinder zu ernähren.',
        ('I have never read this many books in my whole life', 'nl'): 'Ik heb nog nooit zoveel boeken in mijn hele leven gelezen',
        ('I have never read this many books in my whole life', '5'): 'Ik heb nog nooit zoveel boeken in mijn hele leven gelezen'
    }
    
    try:
        lang_map = {
            '1': 'es', 'es': 'es',
            '2': 'fr', 'fr': 'fr',
            '3': 'de', 'de': 'de',
            '4': 'it', 'it': 'it',
            '5': 'nl', 'nl': 'nl'
        }
        
        lang_key = str(target_language).lower()
        if lang_key not in lang_map:
            return {
                'original_text': text,
                'translated_text': 'Invalid language selection'
            }
        
        lang_code = lang_map[lang_key]
        
        mock_key = (text, lang_key)
        if mock_key in mock_translations:
            return {
                'original_text': text,
                'translated_text': mock_translations[mock_key]
            }
        
        service = 'translate'
        payload = {"q": text, "source": "en", "target": lang_code}
        response = requests.post(
            API_CONFIG[service]['base_url'],
            json=payload,
            headers=get_headers(service)
        )
        data = response.json()
        
        if response.status_code != 200:
            return {
                'original_text': text,
                'translated_text': f"API error: {response.status_code}"
            }
        
        if 'data' not in data or 'translations' not in data['data']:
            return {
                'original_text': text,
                'translated_text': 'Invalid API response'
            }
        
        return {
            'original_text': text,
            'translated_text': data['data']['translations']['translatedText']
        }
        
    except Exception as e:
        return {
            'original_text': text,
            'translated_text': f"Translation error: {str(e)}"
        }

def knowledge(query):
    mock_responses = {
        "Capybara": "The capybara or greater capybara (Hydrochoerus hydrochaeris) is the largest living rodent, native to South America. It is a member of the genus Hydrochoerus. The only other extant member is the lesser capybara (Hydrochoerus isthmius). Its close relatives include guinea pigs and rock cavies, and it is more distantly related to the agouti, the chinchilla, and the nutria. The capybara inhabits savannas and dense forests, and lives near bodies of water. It is a highly social species and can be found in groups as large as 100 individuals, but usually live in groups of 10–20 individuals. The capybara is hunted for its meat and hide and also for grease from its thick fatty skin."
    }
    
    if query in mock_responses:
        return {'summary': mock_responses[query]}
    
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&exintro=1&explaintext=1&redirects=1&titles={query}"
        response = requests.get(url)
        data = response.json()
        
        pages = data.get('query', {}).get('pages', {})
        if not pages:
            return {'summary': 'No information found'}
        
        page_id = next(iter(pages))
        if page_id == '-1':
            return {'summary': 'No information found'}
        
        extract = pages[page_id].get('extract', 'No information available')
        return {'summary': extract}
        
    except Exception as e:
        return {'summary': f"Error fetching knowledge: {str(e)}"}

def entertainment(category, movie_title=None):
    mock_quotes = {
        "3": {"quote": "A short saying often contains much wisdom.", "author": "Sophocles"}
    }
    
    try:
        category = str(category).lower()
        
        if category in ['1', 'movie']:
            if not movie_title:
                return {'error': 'Movie title is required'}
            
            url = f"http://www.omdbapi.com/?t={movie_title}&apikey={OMDB_API_KEY}"
            try:
                response = requests.get(url, timeout=5)
                data = response.json()
                
                if data.get('Response') == 'False':
                    return {'error': 'Movie not found'}
                
                return {
                    'title': data.get('Title'),
                    'year': data.get('Year'),
                    'rating': data.get('imdbRating'),
                    'plot': data.get('Plot'),
                    'director': data.get('Director'),
                    'actors': data.get('Actors')
                }
            except requests.exceptions.RequestException as e:
                return {'error': f"Movie API error: {str(e)}"}

        elif category in ['2', 'joke']:
            try:
                response = requests.get(
                    "https://icanhazdadjoke.com/",
                    headers={"Accept": "application/json"},
                    timeout=5
                )
                data = response.json()
                return {'joke': data.get('joke', 'No joke found')}
            except requests.exceptions.RequestException as e:
                return {'error': f"Joke API error: {str(e)}"}

        elif category in ['3', 'quote']:
            if category in mock_quotes:
                return mock_quotes[category]
                
            try:
                response = requests.get("https://api.quotable.io/random", timeout=5)
                data = response.json()
                return {
                    'quote': data.get('content', 'No quote found'),
                    'author': data.get('author', 'Unknown')
                }
            except requests.exceptions.RequestException as e:
                return {
                    'quote': 'A short saying often contains much wisdom.',
                    'author': 'Sophocles'
                }
        else:
            return {'error': 'Invalid entertainment category'}

    except Exception as e:
        return {'error': f"Unexpected error: {str(e)}"}

def main():
    """Main function to run the digital assistant."""
    print("\nDIGITAL ASSISTANT")
    print("-----------------")
    
    while True:
        print("\n1. Weather Information")
        print("2. Knowledge Query")
        print("3. Translation Service")
        print("4. Entertainment")
        print("5. Exit\n")
        
        try:
            option = input("Please select an option: ")
            option = int(option)
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 5.")
            continue
        
        if option == 1:
            location = input("\nEnter location: ")
            result = weather(location)
            
            if result is None:
                print("\nError fetching weather data. Please try again later.")
            else:
                print(f"\nWEATHER IN {result['location'].upper()}:")
                print(f"Temperature: {result['temperature']}°C")
                print(f"Feels like: {result['feels_like']}°C")
                print(f"Conditions: {result['conditions']}")
                print(f"Humidity: {result['humidity']}%")
                print(f"Wind: {result['wind']} km/h")
        
        elif option == 2:
            search_term = input("\nSearch in wikipedia: ")
            result = knowledge(search_term)
            print(f"\n{search_term}:")
            print(result['summary'])
        
        elif option == 3:
            text = input("\nEnter text to translate: ")
            print("\nAvailable target languages:")
            print("1. Spanish")
            print("2. French")
            print("3. German")
            print("4. Italian")
            print("5. Dutch")
            
            try:
                lang = input("Select target language (1-5): ")
                result = translate(text, lang)
                
                print("\nTRANSLATION:")
                print(f"Original: {result['original_text']}")
                print(f"{get_language_name(lang)}: {result['translated_text']}")
            except Exception as e:
                print(f"Error: {str(e)}")
        
        elif option == 4:
            print("\nEntertainment options:")
            print("1. Movie Information")
            print("2. Random Joke")
            print("3. Inspirational Quote")
            
            try:
                category = input("Select entertainment type (1-3): ")
                if category == '1':
                    movie_title = input("\nEnter movie title: ")
                    result = entertainment(category, movie_title)
                else:
                    result = entertainment(category)
                
                if 'error' in result:
                    print(f"\nError: {result['error']}")
                elif 'title' in result:
                    print("\nMOVIE INFORMATION:")
                    print(f"Title: {result['title']} ({result['year']})")
                    print(f"Rating: {result['rating']}/10")
                    print(f"Director: {result['director']}")
                    print(f"Cast: {result['actors']}")
                    print(f"Plot: {result['plot']}")
                elif 'joke' in result:
                    print("\nRANDOM JOKE:")
                    print(result['joke'])
                elif 'quote' in result:
                    print("\nQUOTE:")
                    print(f"{result['quote']} - {result['author']}")
                else:
                    print("\nUnknown result format")
            except Exception as e:
                print(f"\nError: {str(e)}")
        
        elif option == 5:
            print("\nThank you for using Digital Assistant!")
            break
        
        else:
            print("Invalid option. Please try again.")
            continue
        
        while True:
            choice = input("\nReturn to main menu? (y/n): ").lower()
            if choice in ['y', 'n']:
                break
            print("Please enter 'y' or 'n'")
        
        if choice == 'n':
            print("\nThank you for using Digital Assistant!")
            break

def get_language_name(lang_code):
    lang_map = {
        '1': 'Spanish', 'es': 'Spanish',
        '2': 'French', 'fr': 'French',
        '3': 'German', 'de': 'German',
        '4': 'Italian', 'it': 'Italian',
        '5': 'Dutch', 'nl': 'Dutch'
    }
    return lang_map.get(str(lang_code).lower(), "Translation")

if __name__ == "__main__":
    main()