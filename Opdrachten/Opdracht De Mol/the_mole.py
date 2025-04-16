import requests
from bs4 import BeautifulSoup
import time
import os
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options


def get_season(year):
    url = "https://en.wikipedia.org/wiki/De_Mol_(TV_series)"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    tables = soup.find_all("table", {"class": "wikitable"})

    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all(["td", "th"])
            if len(cells) >= 5 and year in row.text:
                mole = cells[3].text.strip()
                winner = cells[4].text.strip()
                location = cells[7].text.strip()
                return mole, winner, location
    return None, None, None

def get_language_code_for_country(country):
    url = f"https://restcountries.com/v3.1/name/{country}"
    response = requests.get(url)

    if response.status_code == 200:
        country_info = response.json()
        languages = country_info[0].get("languages", {})

        if languages:
            lang_code = list(languages.keys())[0]
            return lang_code
        else:
            print(f"Geen talen gevonden voor {country}.")
            return None

def hello(sentence, country):
    url = "https://openl-translate.p.rapidapi.com/translate"
    lang_code = get_language_code_for_country(country)

    if lang_code is None:
        print(f"Kan geen vertaling uitvoeren voor {country}.")
        return None

    payload = {
        "target_lang": lang_code[:2],
        "text": sentence
    }

    headers = {
        "x-rapidapi-key": "a69cdae89amshdb1eb1b1b44f30bp1f4e96jsn8f47560ad780",
        "x-rapidapi-host": "openl-translate.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.text

def get_news(year, location):
    search_term = f"de+mol+{year}+{location.lower()}"
    url = f"https://newsmonkey.be/?s={search_term}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    articles = soup.find_all("h1", {"class":"hentry-title"})
    titles = [a.text.strip() for a in articles[:5]]
    return "\n".join(titles)

def get_info(year, mole):
    base_url = f"https://www.wieisdemol.be/archief/{year}/"
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, "html.parser")

    profile_link = ""
    kandidaten_blokken = soup.find_all("div", class_="col-sm-6")
    for blok in kandidaten_blokken:
        naam_tag = blok.find("b")
        if naam_tag:
            naam = naam_tag.text.strip().lower()
            if mole.lower() == naam:
                a_tag = blok.find("a", href=True)
                if a_tag:
                    profile_link = a_tag["href"]
                    break

    if not profile_link:
        return "Mol niet gevonden."

    if not profile_link.startswith("http"):
        profile_link = "https://www.wieisdemol.be" + profile_link

    profile_response = requests.get(profile_link)
    profile_soup = BeautifulSoup(profile_response.content, "html.parser")
    info_text = "Geen info gevonden."

    top10_row = profile_soup.find("div", class_="row top10")
    if top10_row:
        right_div = top10_row.find("div", class_="col-sm-8")
        if right_div:
            eigenschappen = right_div.find_all("p", class_="eigenschap")
            info_text = "\n".join(p.get_text(strip=True) for p in eigenschappen)

    img_tag = profile_soup.find("img", class_="img-responsive kandidaatimg")
    if img_tag and "src" in img_tag.attrs:
        img_url = img_tag["src"]
        if not img_url.startswith("http"):
            img_url = "https://www.wieisdemol.be" + img_url.replace("..", "")
        img_data = requests.get(img_url).content
        filename = mole.lower().replace(' ', '_') + ".png"
        with open(filename, "wb") as f:
            f.write(img_data)
        info_text+=f"\nImage saved as {filename}"

    info_text = info_text.replace("Leeftijd:", "Leeftijd: ")
    info_text = info_text.replace("Woonplaats:", "Woonplaats: ")

    return info_text

# def get_statistics(year):
#     print("")

def main():
    year = input()

    mole, winner, location = get_season(year)
    if not mole or not winner or not location:
        print("Geen gegevens gevonden voor dat jaar.")
        return

    print(f"The Mole: {mole}")
    print(f"Winner: {winner}")
    print(f"Location: {location}\n")

    translated = hello("Best friends...", location)
    print(translated.strip() + "\n")

    news = get_news(year, location)
    print(news + "\n")

    mol_info = get_info(year, mole)
    print(mol_info)

if __name__ == "__main__":
    main()