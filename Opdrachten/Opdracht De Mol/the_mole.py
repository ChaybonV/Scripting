import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os
import json

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

# def hello(sentence, country):
#     url = "https://google-translate113.p.rapidapi.com/api/v1/translator/text"
#     headers = {
#         "x-rapidapi-key": "a69cdae89amshdb1eb1b1b44f30bp1f4e96jsn8f47560ad780",
#         "x-rapidapi-host": "google-translate113.p.rapidapi.com",
#         "Content-Type": "application/x-www-form-urlencoded"
#     }

#     payload = {
#         "from": "auto",
#         "to": "auto",
#         "text": sentence
#     }

#     response = requests.post(url, data=payload, headers=headers)
#     result = response.json()
#     return result["translated_text"]

def get_news(year, location):
    search_term = f"de+mol+{year}+{location.lower()}"
    url = f"https://newsmonkey.be/?s={search_term}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    articles = soup.find_all("h1", {"class":"hentry-title"})
    titles = [a.text.strip() for a in articles[:5]]
    return "\n".join(titles)

def get_info(year, mole):
    url = "https://www.wieisdemol.be/archief"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    kandidaten = soup.find_all("div", class_="contestant-card")

    for kandidaat in kandidaten:
        naam = kandidaat.find("div", class_="contestant-name").text.strip()
        if naam.lower() == mole.lower():
            details = kandidaat.find("div", class_="contestant-details").text.strip()
            img_tag = kandidaat.find("img")
            img_url = "https://www.wieisdemol.be" + img_tag["src"]
            image_data = requests.get(img_url).content
            with open(f"{mole.lower().replace(' ', '_')}.png", "wb") as f:
                f.write(image_data)
            return details

    return "Mole not found."

def find_excel_buttons(driver):
    return [b for b in driver.find_elements(By.TAG_NAME, "button") if "Excel" in b.text]

def click_button(driver, button):
    try:
        button.click()
        return True
    except:
        return False

def check_downloads(download_dir):
    return [f for f in os.listdir(download_dir) if f.endswith(".xls") or f.endswith(".xlsx")]

def get_statistics(year):
    url = f"https://www.cim.be/nl/televisie?type=yearly_top_100&year={year}&region=north"
    current_dir = os.getcwd()

    options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": current_dir}
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    try:
        print("Waiting for page to load...")
        time.sleep(10)
        excel_buttons = find_excel_buttons(driver)
        if excel_buttons:
            for button in excel_buttons:
                success = click_button(driver, button)
                if success:
                    print("Clicked Excel button")
                    time.sleep(3)
                    break
        else:
            print("No Excel buttons found. Is the mole responsible?")

        print("Checking for downloaded files...")
        time.sleep(3)
        recent_files = check_downloads(current_dir)
        if recent_files:
            newest_file = max(recent_files, key=lambda x: os.path.getctime(os.path.join(current_dir, x)))
            df = pd.read_excel(os.path.join(current_dir, newest_file))
            mol_df = df[df["Programma"].str.contains("De Mol", na=False)]
            best = mol_df.sort_values(by="Kijkers", ascending=False).iloc[0]
            return best["Datum"], best["Kijkers"]
        else:
            return None, None
    finally:
        driver.quit()

def main():
    year = input("Enter year: ").strip()
    mole, winner, location = get_season(year)
    print(f"\nThe Mole: {mole}\nWinner: {winner}\nLocation: {location}\n")

    translated = hello("Best friends...", location)
    print(translated, "\n")

    print("News articles:")
    news = get_news(year, location)
    for title in news:
        print(title)

    print()
    info = get_info(year, mole)
    print(info)
    print(f"Image saved as {mole.lower().replace(' ', '_')}.png\n")

    date, viewers = get_statistics(year)
    if date and viewers:
        print(f"Best episode on {date}\nViewers: {viewers}")
    else:
        print("No statistics found.")

if __name__ == "__main__":
    main()