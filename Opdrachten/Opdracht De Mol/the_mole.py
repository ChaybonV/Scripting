import requests
from bs4 import BeautifulSoup
import os
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import requests
from bs4 import BeautifulSoup

def get_season(year):
    url = "https://en.wikipedia.org/wiki/De_Mol_(TV_series)"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    tables = soup.find_all('table', {'class': 'wikitable'})

    for table in tables:
        rows = table.find_all('tr')
        headers = rows[0].find_all('th')
        header_texts = [header.text.strip() for header in headers]

        if 'Series' in header_texts and 'Premiere' in header_texts and 'Finale' in header_texts:
            for row in rows[1:]:
                cells = row.find_all('td')
                if len(cells) > 0:
                    premiere = cells[1].text.strip()
                    premiere_reversed = premiere[::-1]
                    year_reversed = premiere_reversed[:4]
                    year_good = year_reversed[::-1]

                    if year_good == year:
                        mole = cells[4].text.strip()
                        winner = cells[5].text.strip()
                        location = cells[8].text.strip()
                        return mole,winner,location

    return "Data not found", "Data not found", "Data not found"

# def hello(sentence, country):
#     url = "https://translateai.p.rapidapi.com/google/translate/json"
#     payload = {
#         "origin_language": "en",
#         "target_language": country,
#         "words_not_to_translate": "Earbuds; New York",
#         "paths_to_exclude": "product.media.img_desc",
#         "common_keys_to_exclude": "name; price",
#         "json_content": {
#             "product": {
#                 "productName": "Wireless Earbuds",
#                 "price": "$79 (Seventy Nine)",
#                 "productDesc": sentence,
#                 "manufacturer": { "name": "SoundTech" },
#                 "supplier": { "name": "FastTech" },
#                 "media": {
#                     "img_url": "https://example.com/images/earbuds1.jpg",
#                     "img_desc": "Not to translate"
#                 },
#                 "customer": {
#                     "name": "Alice Johnson",
#                     "location": "New York, USA",
#                     "feedback": "Great quality, easy to connect! Also the shop is inside to the New York city, which is great."
#                 }
#             }
#         }
#     }
#     headers = {
#         "x-rapidapi-key": "a69cdae89amshdb1eb1b1b44f30bp1f4e96jsn8f47560ad780",
#         "x-rapidapi-host": "translateai.p.rapidapi.com",
#         "Content-Type": "application/json"
#     }
#     response = requests.post(url, json=payload, headers=headers)
#     data = response.json()
#     return data.get("translatedText", sentence)

def get_news(year, location):
    search_query = f"de mol {year} {location}"
    url = f"https://newsmonkey.be/?s={search_query}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    articles = soup.find_all('h2', class_='entry-title')
    news_titles = [article.get_text().strip() for article in articles[:5]]
    return news_titles

def get_info(year, mole):
    url = f"https://www.wieisdemol.be/archief/{year}/{mole}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    mole_info = soup.find('div', {'class': 'content'}).get_text(strip=True) if soup.find('div', {'class': 'content'}) else "No info available"

    image_url = soup.find('img', {'class': 'mole-photo'})['src'] if soup.find('img', {'class': 'mole-photo'}) else None
    if image_url:
        img_response = requests.get(image_url)
        img_name = f"{mole.lower().replace(' ', '_')}.png"
        with open(img_name, 'wb') as file:
            file.write(img_response.content)
        return mole_info, img_name
    else:
        return mole_info, None

def get_statistics(year):
    url = f"https://www.cim.be/nl/televisie?type=yearly_top_100&year={year}&region=north"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    stats_table = soup.find('table', {'class': 'table'})
    if stats_table:
        episode_rows = stats_table.find_all('tr')[1:]
        most_watched_episode = episode_rows[0]
        date = most_watched_episode.find_all('td')[0].text.strip()
        viewers = most_watched_episode.find_all('td')[1].text.strip()
        return date, viewers
    else:
        return "No data found", "No data found"

def setup_firefox_options(download_dir):
    options = Options()
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.dir", download_dir)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf;application/vnd.ms-excel;application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    return options

def main():
    year = input("Enter the year of the season to analyze: ")
    
    mole, winner, location = get_season(year)
    print(f"The Mole: {mole}")
    print(f"Winner: {winner}")
    print(f"Location: {location}")
    
    # sentence = "Best friends..."
    # country = "fr"  # Change to appropriate country code for the location
    # translated_sentence = hello(sentence, country)
    # print(f"{sentence} -> {translated_sentence}")
    
    news_titles = get_news(year, location)
    for title in news_titles:
        print(title)
    
    mole_info, mole_img = get_info(year, mole)
    print(f"Mole Info: {mole_info}")
    if mole_img:
        print(f"Image saved as {mole_img}")
    
    date, viewers = get_statistics(year)
    print(f"Best episode on {date}")
    print(f"Viewers: {viewers}")

if __name__ == "__main__":
    main()