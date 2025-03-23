import os
import csv
import re
from fpdf import FPDF

def count_character_dialogue(movie):
    """Tel hoe vaak elk personage spreekt in de film."""
    dialogue_count = {}
    srt_file = os.path.join('Pixar', f'{movie}.srt')  # Pad naar het .srt-bestand
    if not os.path.exists(srt_file):
        print(f"Bestand niet gevonden: {srt_file}")
        return {}

    with open(srt_file, 'r', encoding='utf-8-sig') as file:
        lines = file.readlines()
        for line in lines:
            match = re.match(r'^([A-Za-z]+):', line)
            if match:
                character = match.group(1)
                dialogue_count[character] = dialogue_count.get(character, 0) + 1
    return dialogue_count

def count_quote(movie, quote):
    """Tel hoe vaak een specifieke zin voorkomt en geef de timestamps terug."""
    timestamps = []
    count = 0
    srt_file = os.path.join('Pixar', f'{movie}.srt')  # Pad naar het .srt-bestand
    if not os.path.exists(srt_file):
        print(f"Bestand niet gevonden: {srt_file}")
        return 0, []

    with open(srt_file, 'r', encoding='utf-8-sig') as file:
        lines = file.readlines()
        for i in range(len(lines)):
            if quote.lower() in lines[i].lower():
                count += 1
                timestamps.append(lines[i - 1].strip())  # Voeg de vorige regel (timestamp) toe
    return count, timestamps

def analyze_actors(actor):
    """Zoek alle films waarin een acteur een personage heeft ingesproken en sorteer op IMDb-rating."""
    movies_dict = {}
    csv_file = os.path.join('Pixar', 'pixar_movies.csv')  # Pad naar het CSV-bestand
    with open(csv_file, 'r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            print(row)  # Debug: print elke rij
            if actor in row['main_voice_actors']:
                movies_dict[row['movie']] = float(row['imdb_rating'])
    return dict(sorted(movies_dict.items(), key=lambda item: item[1], reverse=True))

def calculate_success(movie):
    """Bereken de financiële succesratio van een film."""
    csv_file = os.path.join('Pixar', 'pixar_movies.csv')  # Pad naar het CSV-bestand
    with open(csv_file, 'r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['movie'] == movie:
                budget = float(row['budget'].strip('$').replace(',', ''))
                box_office = float(row['total_worldwide_gross_sales'].strip('$').replace(',', ''))
                success_ratio = box_office / budget
                if success_ratio >= 5.0:
                    category = 'Blockbuster'
                elif 3.0 <= success_ratio < 5.0:
                    category = 'Very Successful'
                elif 2.0 <= success_ratio < 3.0:
                    category = 'Successful'
                elif 1.0 <= success_ratio < 2.0:
                    category = 'Break-even or slightly profitable'
                else:
                    category = 'Loss'
                return budget, box_office, success_ratio, category
    return None, None, None, None

def generate_movie_pdf(movie):
    """Genereer een PDF-rapport voor een film."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    csv_file = os.path.join('Pixar', 'pixar_movies.csv')  # Pad naar het CSV-bestand
    with open(csv_file, 'r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['movie'] == movie:
                pdf.cell(200, 10, txt=f"Movie: {row['movie']}", ln=True)
                pdf.cell(200, 10, txt=f"Plot Summary: {row['plot_summary']}", ln=True)
                pdf.cell(200, 10, txt=f"Director: {row['director']}", ln=True)
                pdf.cell(200, 10, txt=f"Genre: {row['movie_genre']}", ln=True)
                break
    pdf.output(os.path.join('Pixar', f"{movie}_report.pdf"))  # Sla de PDF op in de Pixar-map

def main():
    # Vraag de gebruiker om een film en een zin om te zoeken
    movie = input("Voer de naam van een Pixar-film in (bijv. 'Finding Nemo'): ")
    quote = input("Voer een zin in om te zoeken (bijv. 'just keep swimming'): ")

    # Analyseer de film
    dialogue_count = count_character_dialogue(movie)
    print(f"\n{movie}")
    for character, count in dialogue_count.items():
        print(f"{character}: {count} times")

    count, timestamps = count_quote(movie, quote)
    print(f"\n'{quote}' appears {count} times")
    for timestamp in timestamps:
        print(f"- {timestamp}")

    budget, box_office, success_ratio, category = calculate_success(movie)
    print(f"\nBudget = {budget}")
    print(f"Box office = {box_office}")
    print(f"Success Ratio = {success_ratio:.2f}")
    print(f"Success Category = {category}")

    # Genereer een PDF-rapport
    generate_movie_pdf(movie)
    print(f"\nPDF generated: Pixar/{movie}_report.pdf")

if __name__ == "__main__":
    main()