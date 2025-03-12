import re
import datetime
import qrcode
from tabulate import tabulate


def is_valid_number(register_number):
    """Controleert of een Belgisch rijksregisternummer geldig is."""
    pattern = r"^\d{2}\.\d{2}\.\d{2}-\d{3}\.\d{2}$"
    if not re.match(pattern, register_number):
        return False  # Fout: verkeerd formaat

    # Verwijder scheidingstekens
    numbers_only = register_number.replace(".", "").replace("-", "")
    
    birth_part = numbers_only[:6]
    sequence_part = numbers_only[6:9]
    check_digits = int(numbers_only[9:])

    # Controleer of geboortedatum geldig is
    try:
        year = int(birth_part[:2])
        month = int(birth_part[2:4])
        day = int(birth_part[4:6])
        
        full_year = 2000 + year if int(numbers_only[0]) in [0, 1] else 1900 + year
        birth_date = datetime.date(full_year, month, day)
        
        if birth_date > datetime.date.today():
            return False  # Fout: toekomstige geboortedatum
    except ValueError:
        return False  # Fout: ongeldige datum

    # Checksum berekenen
    base_number = int(numbers_only[:9])
    if full_year >= 2000:
        base_number += 2000000000

    calculated_check_digits = 97 - (base_number % 97)
    
    return calculated_check_digits == check_digits


def check_number(register_number):
    """Geeft een geldigheidsstatus en reden."""
    if not is_valid_number(register_number):
        return "invalid register number - incorrect formatting, invalid date, future birth date, or incorrect check digits"

    # Verkrijg registratiedetails
    numbers_only = register_number.replace(".", "").replace("-", "")
    birth_part = numbers_only[:6]
    sequence_part = int(numbers_only[6:9])

    # Bepaal generatie
    year_prefix = 2000 if int(numbers_only[0]) in [0, 1] else 1900
    birth_year = year_prefix + int(birth_part[:2])

    if birth_year < 1940:
        generation = "pre-war generation"
    elif birth_year <= 1945:
        generation = "war generation"
    elif birth_year <= 1964:
        generation = "baby boomers"
    elif birth_year <= 1979:
        generation = "generation X"
    elif birth_year <= 1995:
        generation = "millennials"
    elif birth_year <= 2010:
        generation = "generation Z"
    else:
        generation = "generation Alpha"

    # Bepaal vroege/late registratie
    if 1 <= sequence_part <= 100:
        return f"valid register number (early) - {generation}"
    elif 900 <= sequence_part <= 999:
        return f"valid register number (late) - {generation}"
    else:
        return f"valid register number - {generation}"


def structured_info(register_number):
    """Toont gestructureerde info over het rijksregisternummer."""
    numbers_only = register_number.replace(".", "").replace("-", "")
    birth_part = numbers_only[:6]
    sequence_part = int(numbers_only[6:9])

    # Bereken geboortedatum
    year_prefix = 2000 if int(numbers_only[0]) in [0, 1] else 1900
    birth_year = year_prefix + int(birth_part[:2])
    birth_month = int(birth_part[2:4])
    birth_day = int(birth_part[4:6])
    birth_date = datetime.date(birth_year, birth_month, birth_day)

    # Bepaal leeftijd
    today = datetime.date.today()
    age = today.year - birth_year - ((today.month, today.day) < (birth_month, birth_day))

    # Bepaal geslacht
    gender = "Male" if sequence_part % 2 != 0 else "Female"

    # Bepaal generatie
    generation = check_number(register_number).split("-")[-1].strip()

    # Tabelleren
    table = [
        ["Date of Birth", birth_date.strftime("%B %d, %Y")],
        ["Gender", gender],
        ["Age", age],
        ["Generation", generation],
    ]

    print(tabulate(table, headers=["Field", "Value"], tablefmt="grid"))


def generate_qr(register_number):
    """Genereert een QR-code voor het rijksregisternummer."""
    img = qrcode.make(register_number)
    img.save(f"{register_number}.png")
    print(f"image saved --> {register_number}.png")


def get_names(date_of_birth, gender):
    """Geeft de top 5 meest voorkomende namen uit de bijbehorende tekstbestanden."""
    file_name = "male.txt" if gender.lower() == "male" else "female.txt"

    try:
        with open(file_name, "r", encoding="utf-8") as f:
            names = [line.strip() for line in f.readlines()]
        
        # Top 5 namen teruggeven
        print(names[:5])
    except FileNotFoundError:
        print(f"File {file_name} not found!")


def main():
    """Hoofdprogramma."""
    register_number = input("Enter number: ").strip()
    validity = check_number(register_number)
    print(validity)

    if "invalid" in validity:
        return  # Stop als het nummer ongeldig is

    output_type = input("Enter output (table, qr-code, name): ").strip().lower()

    if output_type == "table":
        structured_info(register_number)
    elif output_type == "qr-code":
        generate_qr(register_number)
    elif output_type == "name":
        numbers_only = register_number.replace(".", "").replace("-", "")
        birth_part = numbers_only[:6]
        sequence_part = int(numbers_only[6:9])

        year_prefix = 2000 if int(numbers_only[0]) in [0, 1] else 1900
        birth_year = year_prefix + int(birth_part[:2])
        birth_month = int(birth_part[2:4])
        birth_day = int(birth_part[4:6])

        gender = "Male" if sequence_part % 2 != 0 else "Female"
        get_names(datetime.date(birth_year, birth_month, birth_day), gender)
    else:
        print("Invalid output type.")


if __name__ == "__main__":
    main()