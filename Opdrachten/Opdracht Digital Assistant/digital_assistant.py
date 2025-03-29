import requests
import json
import re
import time

RAPIDAPI_KEY = "a69cdae89amshdb1eb1b1b44f30bp1f4e96jsn8f47560ad780"
OMDB_API_KEY = "5fc50607"

def weather(location):
    try:
        url = f"https://open-weather13.p.rapidapi.com/city/{location}"
        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": "open-weather13.p.rapidapi.com"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 429:
            print(f"Error: Too many requests. Please try again later.")
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
        
        url = "https://deep-translate1.p.rapidapi.com/language/translate/v2"
        
        payload = {
            "q": text,
            "source": "en",
            "target": lang_code
        }
        
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": "deep-translate1.p.rapidapi.com"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            translated_text = data.get('data', {}).get('translations', [])
            
            if isinstance(translated_text, list) and len(translated_text) > 0:
                translated_text = translated_text[0].get('translatedText', 'No translation found')
            elif isinstance(translated_text, dict):
                translated_text = translated_text.get('translatedText', 'No translation found')
            else:
                translated_text = 'No translation found'
            
            if isinstance(translated_text, list):
                translated_text = translated_text[0] if len(translated_text) > 0 else 'No translation found'
            
            return {
                'original_text': text,
                'translated_text': translated_text
            }
            
        elif response.status_code == 403:
            return {
                'original_text': text,
                'translated_text': 'API access denied (invalid key or quota exceeded)'
            }
        elif response.status_code == 429:
            return {
                'original_text': text,
                'translated_text': 'Too many requests. Please try again later.'
            }
        else:
            return {
                'original_text': text,
                'translated_text': f'Translation error (HTTP {response.status_code})'
            }
        
    except requests.exceptions.RequestException as e:
        return {
            'original_text': text,
            'translated_text': 'Translation service unavailable. Please try again later.'
        }
    except Exception as e:
        return {
            'original_text': text,
            'translated_text': f'Translation error: {str(e)}'
        }

def knowledge(query):
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
            try:
                response = requests.get("https://api.quotable.io/random", timeout=5)
                data = response.json()
                return {
                    'quote': data.get('content', 'No quote found'),
                    'author': data.get('author', 'Unknown')
                }
            except requests.exceptions.RequestException as e:
                return {'error': f"Quote API error: {str(e)}"}
        else:
            return {'error': 'Invalid entertainment category'}

    except Exception as e:
        return {'error': f"Unexpected error: {str(e)}"}

def get_language_name(lang_code):
    lang_map = {
        '1': 'Spanish', 'es': 'Spanish',
        '2': 'French', 'fr': 'French',
        '3': 'German', 'de': 'German',
        '4': 'Italian', 'it': 'Italian',
        '5': 'Dutch', 'nl': 'Dutch'
    }
    return lang_map.get(str(lang_code).lower(), "Translation")

def main():
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

if __name__ == "__main__":
    main()