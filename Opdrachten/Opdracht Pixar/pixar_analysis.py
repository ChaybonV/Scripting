import os
import re
import csv
import zipfile
from pathlib import Path
from fpdf import FPDF

def extract_zip(zip_file="Pixar.zip"):
    extract_path = "PixarData"

    if not os.path.exists(extract_path):
        os.makedirs(extract_path)
    
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    
    return extract_path

def load_movie_data(extract_path):
    movies_data = {}
    movie_info = {}
    movies_csv_path = os.path.join(extract_path, "pixar_movies.csv")

    with open(movies_csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            movie_name = row["movie"]
            movies_data[movie_name] = row
    
    info_csv_path = os.path.join(extract_path, "pixar_info.csv")
    with open(info_csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            movie_name = row["film"]
            movie_info[movie_name] = row
    
    return movies_data, movie_info

def count_character_dialogue(movie):
    extract_path = extract_zip()
    movies_data, _ = load_movie_data(extract_path)
    movie_name = next((name for name in movies_data.keys() if name.lower() == movie.lower()), movie)

    if movie_name not in movies_data:
        main_characters = [char.strip() for char in movies_data[list(movies_data.keys())[0]]["main_characters"].split(",")]
        return {char: 0 for char in main_characters}

    main_characters = [char.strip() for char in movies_data[movie_name]["main_characters"].split(",")]
    subtitle_files = [f for f in os.listdir(extract_path) if f.endswith(".srt")]
    movie_file = None

    for file in subtitle_files:
        file_name = file[:-4].replace("_", " ")
        if file_name.lower() == movie_name.lower().replace(".", " "):
            movie_file = file
            break

    if not movie_file:
        return {char: 0 for char in main_characters}

    character_counts = {char: 0 for char in main_characters}

    try:
        with open(os.path.join(extract_path, movie_file), 'r', encoding='utf-8-sig', errors='ignore') as f:
            for line in f:
                for character in main_characters:
                    if re.search(r'\b' + re.escape(character) + r'\b', line, re.IGNORECASE):
                        character_counts[character] += 1
    except Exception:
        pass

    return character_counts

def count_quote(movie, quote):
    if not quote or quote.lower() == movie.lower():
        return 0, []

    extract_path = extract_zip()
    subtitle_files = [f for f in os.listdir(extract_path) if f.endswith(".srt")]
    movie_file = None
    
    for file in subtitle_files:
        file_name_clean = file[:-4].replace(".", " ")
        movie_name_clean = movie.replace(".", " ")
        if file_name_clean.lower() == movie_name_clean.lower():
            movie_file = file
            break

    if not movie_file:
        return 0, []

    timestamps = []

    try:
        with open(os.path.join(extract_path, movie_file), 'r', encoding='utf-8-sig', errors='ignore') as f:
            lines = f.readlines()

            timestamp = None
            dialogue_lines = []

            for line in lines:
                line = line.strip()
                if re.match(r'^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$', line):
                    timestamp = line
                    dialogue_lines = []
                    continue

                if line:
                    dialogue_lines.append(line)

                if not line and timestamp and dialogue_lines:
                    full_dialogue = " ".join(dialogue_lines)
                    if quote.lower() in full_dialogue.lower():
                        timestamps.append((timestamp, quote))
                    timestamp = None
                    dialogue_lines = []

    except Exception:
        pass

    return len(timestamps), timestamps

def analyze_actors(actor):
    extract_path = extract_zip()
    movies_data, _ = load_movie_data(extract_path)
    actor_movies = []
    
    for movie, data in movies_data.items():
        voice_actors = [a.strip() for a in data["main_voice_actors"].split(",")]
        if any(actor.lower() == a.lower() for a in voice_actors):
            actor_movies.append({
                'title': movie,
                'imdb_rating': float(data["imdb_rating"].split('/')[0])
            })
    
    actor_movies.sort(key=lambda x: x['imdb_rating'], reverse=True)
    return actor_movies

def calculate_success(movie):
    extract_path = extract_zip()
    movies_data, movie_info = load_movie_data(extract_path)
    movie_name = movie

    for name in movies_data.keys():
        if name.lower() == movie.lower():
            movie_name = name
            break
    
    movie_data = None
    for name, data in movie_info.items():
        if name.lower() == movie.lower():
            movie_data = data
            break
    
    if not movie_data:
        return {'title': movie_name,'budget': 0,'box_office': 0,'success_ratio': 0,'success_category': "Loss (less than budget)"}
    
    try:
        budget = int(movie_data["budget"].replace(",", ""))
        box_office = int(movie_data["box_office_worldwide"].replace(",", ""))
    except (ValueError, KeyError):
        return {'title': movie_name,'budget': 0,'box_office': 0,'success_ratio': 0,'success_category': "Loss (less than budget)"}
    
    ratio = box_office / budget if budget > 0 else 0
    ratio_rounded = round(ratio, 2)
    
    if ratio >= 5.0:
        category = "Blockbuster (5x+ budget)"
    elif 3.0 <= ratio < 5.0:
        category = "Very successful (3-5x budget)"
    elif 2.0 <= ratio < 3.0:
        category = "Successful (2-3x budget)"
    elif 1.0 <= ratio < 2.0:
        category = "Break-even or slightly profitable (1-2x budget)"
    else:
        category = "Loss (less than budget)"
    
    return {'title': movie_name,'budget': budget,'box_office': box_office,'success_ratio': ratio_rounded,'success_category': category}

def generate_movie_pdf(movie):
    extract_path = extract_zip()
    movies_data, movie_info = load_movie_data(extract_path)
    movie_name = movie
    movie_data = None

    for name, data in movies_data.items():
        if name.lower() == movie.lower():
            movie_data = data
            movie_name = name
            break
    
    if not movie_data:
        movie_data = {'date_released': 'N/A','director': 'N/A','movie_genre': 'N/A','movie_rating': 'N/A','imdb_rating': 'N/A','plot_summary': 'No plot summary available.'}
    
    success_info = calculate_success(movie)
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, movie_name, ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Movie Information", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, f"Release Date: {movie_data['date_released']}")
    pdf.multi_cell(0, 10, f"Director: {movie_data['director']}")
    pdf.multi_cell(0, 10, f"Genre: {movie_data['movie_genre']}")
    pdf.multi_cell(0, 10, f"Rating: {movie_data['movie_rating']}")
    pdf.multi_cell(0, 10, f"IMDb Rating: {movie_data['imdb_rating']}")
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Plot Summary", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, movie_data['plot_summary'])
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Financial Information", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, f"Budget: ${success_info['budget']:,}")
    pdf.multi_cell(0, 10, f"Box Office: ${success_info['box_office']:,}")
    pdf.multi_cell(0, 10, f"Success Ratio: {success_info['success_ratio']:.2f}")
    pdf.multi_cell(0, 10, f"Success Category: {success_info['success_category']}")
    pdf_filename = f"{movie_name.replace(' ', '_')}_report.pdf"
    pdf.output(pdf_filename)
    
    return pdf_filename

def main():
    movie = input("Enter a Pixar movie name: ")
    print()
    
    character_counts = count_character_dialogue(movie)
    for character, count in character_counts.items():
        print(f"{character}: {count} times")
    print()
    
    if character_counts and list(character_counts.values()) != [0] * len(character_counts):
        quote = input("Enter a quote to search for: ")
        print()
        
        count, timestamps = count_quote(movie, quote)
        if count > 0:
            print(f"The quote appears {count} times")
            for timestamp, quote_text in timestamps:
                print(f"- {timestamp}")
            print()
        else:
            print("No quote asked")
            print()
    else:
        print("No quote asked")
        print()
    
    success_info = calculate_success(movie)
    print(f"Budget = {success_info['budget']}")
    print(f"Box office = {success_info['box_office']}")
    print(f"Success Ratio = {success_info['success_ratio']:.2f}")
    print(f"Success Category = {success_info['success_category']}")
    print()
    pdf_path = generate_movie_pdf(movie)
    print(f"PDF generated: {pdf_path}")

if __name__ == "__main__":
    main()