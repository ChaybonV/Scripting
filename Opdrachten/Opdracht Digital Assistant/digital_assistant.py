import requests
import json

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
            return None
        
        data = response.json()
        
        if response.status_code != 200:
            return None
        
        return {
            'location': f"{data.get('name', location)}, {data.get('sys', {}).get('country', '')}",
            'temperature': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'conditions': data['weather'][0]['description'].title(),
            'humidity': data['main']['humidity'],
            'wind': round(data['wind']['speed'] * 3.6)
        }
    except Exception:
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
                'translated_text': 'Ongeldige taal selectie'
            }
        
        lang_code = lang_map[lang_key]
        service = 'translate'
        payload = {"q": text,"source": "en","target": lang_code}
        response = requests.post(API_CONFIG[service]['base_url'],json=payload,headers=get_headers(service))
        data = response.json()
        
        if response.status_code != 200:
            return {
                'original_text': text,
                'translated_text': f"API fout: {response.status_code}"
            }
        
        if 'data' not in data or 'translations' not in data['data']:
            return {
                'original_text': text,
                'translated_text': 'Ongeldig API antwoord'
            }
        
        return {
            'original_text': text,
            'translated_text': data['data']['translations']['translatedText']
        }
        
    except requests.exceptions.RequestException as e:
        return {
            'original_text': text,
            'translated_text': f"Netwerkfout: {str(e)}"
        }
    except Exception as e:
        return {
            'original_text': text,
            'translated_text': f"Vertalingsfout: {str(e)}"
        }

def knowledge(query):
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&exintro&explaintext&titles={query}"
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
                response = requests.get("https://icanhazdadjoke.com/",headers={"Accept": "application/json"},timeout=5)
                data = response.json()
                return {'joke': data.get('joke', 'No joke found')}
            except requests.exceptions.RequestException as e:
                return {'error': f"Joke API error: {str(e)}"}

        elif category in ['3', 'quote']:
            try:
                response = requests.get("https://api.quotable.io/random",timeout=5)
                data = response.json()
                return {'quote': data.get('content', 'No quote found'),'author': data.get('author', 'Unknown')}
            except requests.exceptions.RequestException as e:
                return {'quote': 'Anticipate the difficult by managing the easy.','author': 'Lao Tzu'}
        else:
            return {'error': 'Invalid entertainment category'}

    except Exception as e:
        return {'error': f"Unexpected error: {str(e)}"}

def main():
    print("\nDIGITALE ASSISTENT")
    print("------------------")
    
    while True:
        print("\n1. Weer informatie")
        print("2. Kennis opzoeken")
        print("3. Vertaal service")
        print("4. Entertainment")
        print("5. Afsluiten\n")
        
        try:
            optie = int(input("Kies een optie (1-5): "))
        except ValueError:
            print("Ongeldige invoer. Voer een nummer in tussen 1 en 5.")
            continue
        
        if optie == 1:
            locatie = input("\nVoer locatie in: ")
            resultaat = weather(locatie)
            
            if isinstance(resultaat, str):
                print(f"\n{resultaat}")
            else:
                print(f"\nWEER IN {resultaat['location'].upper()}:")
                print(f"Temperatuur: {resultaat['temperature']}°C")
                print(f"Voelt als: {resultaat['feels_like']}°C")
                print(f"Omstandigheden: {resultaat['conditions']}")
                print(f"Luchtvochtigheid: {resultaat['humidity']}%")
                print(f"Wind: {resultaat['wind']} km/h")
        
        elif optie == 2:
            search_term = input("\nSearch Wikipedia: ")
            result = knowledge(search_term)
            print(f"\n{search_term}:")
            print(result['summary'])
        
        elif optie == 3:
            tekst = input("\nVoer tekst in om te vertalen: ")
            print("\nBeschikbare doeltalen:")
            print("1. Spaans (es)")
            print("2. Frans (fr)")
            print("3. Duits (de)")
            print("4. Italiaans (it)")
            print("5. Nederlands (nl)")
            
            try:
                taal = input("Kies doeltaal (1-5 of taalcode zoals 'es'): ")
                try:
                    taal_num = int(taal)
                    if taal_num not in range(1, 6):
                        raise ValueError
                    resultaat = translate(tekst, taal_num)
                except ValueError:
                    resultaat = translate(tekst, taal)
                
                print("\nVERTALING:")
                print(f"Origineel: {resultaat['original_text']}")
                print(f"Vertaling: {resultaat['translated_text']}")
            except Exception as e:
                print(f"Fout: {str(e)}")
        
        elif optie == 4:
            print("\nEntertainment options:")
            print("1. Movie Information")
            print("2. Random Joke")
            print("3. Inspirational Quote")
            
            try:
                categorie = input("Select entertainment type (1-3): ")
                if categorie in ['1', 'movie']:
                    film_titel = input("\nEnter movie title: ")
                    resultaat = entertainment(categorie, film_titel)
                else:
                    resultaat = entertainment(categorie)
                
                if 'error' in resultaat:
                    print(f"\nError: {resultaat['error']}")
                elif 'title' in resultaat:
                    print("\nMOVIE INFORMATION:")
                    print(f"Title: {resultaat['title']} ({resultaat['year']})")
                    print(f"Rating: {resultaat['rating']}")
                    print(f"Director: {resultaat['director']}")
                    print(f"Cast: {resultaat['actors']}")
                    print(f"Plot: {resultaat['plot']}")
                elif 'joke' in resultaat:
                    print("\nRANDOM JOKE:")
                    print(resultaat['joke'])
                elif 'quote' in resultaat:
                    print("\nQUOTE:")
                    print(f"{resultaat['quote']} - {resultaat['author']}")
                else:
                    print("\nUnknown result format")
            except Exception as e:
                print(f"\nError: {str(e)}")
        
        elif optie == 5:
            print("\nBedankt voor het gebruiken van de Digitale Assistent!")
            break
        
        else:
            print("Ongeldige optie. Probeer opnieuw.")
            continue
        
        while True:
            keuze = input("\nTerug naar hoofdmenu? (j/n): ").lower()
            if keuze in ['j', 'n']:
                break
            print("Voer 'j' of 'n' in")
        
        if keuze == 'n':
            print("\nBedankt voor het gebruiken van de Digitale Assistent!")
            break

if __name__ == "__main__":
    main()