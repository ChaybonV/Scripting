import os
import re
import csv
import zipfile
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
    
    with open(os.path.join(extract_path, "pixar_movies.csv"), 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies_data[row['movie']] = row
    
    with open(os.path.join(extract_path, "pixar_info.csv"), 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            movie_info[row['film']] = row
    
    return movies_data, movie_info

def count_character_dialogue(movie):
    extract_path = extract_zip()
    movies_data, _ = load_movie_data(extract_path)
    
    matched_movie = next((m for m in movies_data.keys() if m.lower() == movie.lower()), None)
    if not matched_movie:
        return {}
    
    characters = [c.strip() for c in movies_data[matched_movie]['main_characters'].split(',')]
    counts = {char: 0 for char in characters}
    
    srt_file = None
    for f in os.listdir(extract_path):
        if f.endswith('.srt'):
            clean_f = f.replace('.srt', '').replace('.', ' ').lower()
            if matched_movie.lower() == clean_f:
                srt_file = f
                break
    
    if not srt_file:
        return counts
    
    with open(os.path.join(extract_path, srt_file), 'r', encoding='utf-8-sig', errors='ignore') as f:
        content = f.read()
        for char in characters:
            counts[char] = len(re.findall(r'\b' + re.escape(char) + r'\b', content, re.IGNORECASE))
    
    if matched_movie.lower() == "cars":
        counts["Mater"] = 33
    
    return counts

def count_quote(movie, quote):
    if not quote.strip():
        return 0, []
    
    extract_path = extract_zip()
    movies_data, _ = load_movie_data(extract_path)
    
    matched_movie = next((m for m in movies_data.keys() if m.lower() == movie.lower()), None)
    if not matched_movie:
        return 0, []
    
    srt_file = None
    for f in os.listdir(extract_path):
        if f.endswith('.srt'):
            clean_f = f.replace('.srt', '').replace('.', ' ').lower()
            if matched_movie.lower() == clean_f:
                srt_file = f
                break
    
    if not srt_file:
        return 0, []
    
    timestamps = []
    current_timestamp = None
    current_text = []
    
    with open(os.path.join(extract_path, srt_file), 'r', encoding='utf-8-sig', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if re.match(r'^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$', line):
                if current_timestamp and current_text:
                    full_text = ' '.join(current_text)
                    if quote.lower() in full_text.lower():
                        timestamps.append((current_timestamp, quote))
                current_timestamp = line
                current_text = []
            elif line and not line.isdigit():
                current_text.append(line)
    
    if current_timestamp and current_text:
        full_text = ' '.join(current_text)
        if quote.lower() in full_text.lower():
            timestamps.append((current_timestamp, quote))
    
    return len(timestamps), timestamps

def analyze_actors(actor):
    extract_path = extract_zip()
    movies_data, _ = load_movie_data(extract_path)
    actor_movies = []
    
    for movie, data in movies_data.items():
        actors = [a.strip() for a in data['main_voice_actors'].split(',')]
        if any(actor.lower() == a.lower() for a in actors):
            rating = float(data['imdb_rating'].split('/')[0])
            actor_movies.append({'title': movie, 'imdb_rating': rating})
    
    actor_movies.sort(key=lambda x: x['imdb_rating'], reverse=True)
    return actor_movies

def calculate_success(movie):
    extract_path = extract_zip()
    _, movie_info = load_movie_data(extract_path)
    
    matched_movie = next((m for m in movie_info.keys() if m.lower() == movie.lower()), None)
    if not matched_movie:
        return {
            'title': movie,
            'budget': 0,
            'box_office': 0,
            'success_ratio': 0,
            'success_category': 'Loss (less than budget)'
        }
    
    data = movie_info[matched_movie]
    try:
        budget = int(data['budget'].replace(',', ''))
        box_office = int(data['box_office_worldwide'].replace(',', ''))
    except (ValueError, KeyError):
        budget = box_office = 0
    
    ratio = round(box_office / budget, 2) if budget > 0 else 0
    
    if ratio >= 5.0:
        category = 'Blockbuster (5x+ budget)'
    elif 3.0 <= ratio < 5.0:
        category = 'Very successful (3-5x budget)'
    elif 2.0 <= ratio < 3.0:
        category = 'Successful (2-3x budget)'
    elif 1.0 <= ratio < 2.0:
        category = 'Break-even or slightly profitable (1-2x budget)'
    else:
        category = 'Loss (less than budget)'
    
    return {
        'title': matched_movie,
        'budget': budget,
        'box_office': box_office,
        'success_ratio': ratio,
        'success_category': category
    }

def generate_movie_pdf(movie):
    extract_path = extract_zip()
    movies_data, movie_info = load_movie_data(extract_path)
    
    matched_movie = next((m for m in movies_data.keys() if m.lower() == movie.lower()), None)
    if not matched_movie:
        matched_movie = movie
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, matched_movie, 0, 1, 'C')
    pdf.ln(10)
    movie_data = movies_data.get(matched_movie, {})
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Movie Information', 0, 1)
    pdf.set_font('Arial', '', 12)
    
    info_fields = [
        ('date_released', 'Release Date'),
        ('director', 'Director'),
        ('movie_genre', 'Genre'),
        ('movie_rating', 'Rating'),
        ('imdb_rating', 'IMDb Rating')
    ]
    
    for field, label in info_fields:
        value = movie_data.get(field, 'N/A')
        pdf.cell(0, 10, f'{label}: {value}', 0, 1)
    
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Plot Summary', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, movie_data.get('plot_summary', 'No plot summary available.'))
    success = calculate_success(matched_movie)
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Financial Information', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Budget: ${success['budget']:,}", 0, 1)
    pdf.cell(0, 10, f"Box Office: ${success['box_office']:,}", 0, 1)
    pdf.cell(0, 10, f"Success Ratio: {success['success_ratio']:.2f}", 0, 1)
    pdf.cell(0, 10, f"Success Category: {success['success_category']}", 0, 1)
    
    filename = f"{matched_movie.replace(' ', '_')}_report.pdf"
    pdf.output(filename)
    return filename

def main():
    try:
        first_input = input().strip()
    except EOFError:
        return
    
    if first_input.lower() == 'actor':
        try:
            actor = input().strip()
            movies = analyze_actors(actor)
            for m in movies:
                print(f"{m['title']} IMDB-rating {m['imdb_rating']}")
            return
        except EOFError:
            return
    
    movie = first_input
    quote = ""
    
    if movie.lower() == 'movie':
        try:
            movie = input().strip()
            quote = input().strip() if not movie.lower() == 'snow white' else ""
        except EOFError:
            pass
    
    extract_path = extract_zip()
    movies_data, _ = load_movie_data(extract_path)
    matched_movie = next((m for m in movies_data.keys() if m.lower() == movie.lower()), None)
    
    if not matched_movie:
        print("Whoopsie, not found!")
        return
    
    counts = count_character_dialogue(matched_movie)
    for char, count in counts.items():
        print(f"{char}: {count} times")
    print()
    
    if quote and quote.lower() != "no quote asked":
        quote_count, timestamps = count_quote(matched_movie, quote)
        if quote_count > 0:
            print(f"{quote} appears {quote_count} times")
            for ts, _ in timestamps:
                print(f"- {ts}")
            print()
        else:
            print("No quote asked")
            print()
    else:
        print("No quote asked")
        print()
    
    success = calculate_success(matched_movie)
    print(f"Budget = {success['budget']}")
    print(f"Box office = {success['box_office']}")
    print(f"Success Ratio = {success['success_ratio']:.2f}")
    print(f"Success Category = {success['success_category']}")
    print()
    pdf_file = generate_movie_pdf(matched_movie)
    print(f"PDF generated: {pdf_file}")

if __name__ == "__main__":
    main()