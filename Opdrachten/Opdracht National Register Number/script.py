import re
import datetime
import qrcode
from tabulate import tabulate

def is_valid_number(register_number):
    numbers_only = register_number.replace(".", "").replace("-", "")
    if len(numbers_only) != 11:
        return "invalid length"

    pattern = r"^\d{2}\.\d{2}\.\d{2}-\d{3}[-.]\d{2}$"
    if not re.match(pattern, register_number):
        return "incorrect formatting"

    birth_part = numbers_only[:6]
    check_digits = int(numbers_only[9:])
    year = int(birth_part[:2])
    month = int(birth_part[2:4])
    day = int(birth_part[4:6])
    full_year_1900 = 1900 + year
    full_year_2000 = 2000 + year

    try:
        birth_date_1900 = datetime.date(full_year_1900, month, day)
    except ValueError:
        return "invalid date"
    
    try:
        birth_date_2000 = datetime.date(full_year_2000, month, day)
    except ValueError:
        pass
    
    today = datetime.date.today()
    if birth_date_1900 > today:
        return "future birth date"
    
    full_year = full_year_2000 if birth_date_2000 <= today else full_year_1900
    base_number = int(numbers_only[:9])

    if full_year >= 2000:
        base_number += 2000000000

    calculated_check_digits = 97 - (base_number % 97)
    if calculated_check_digits != check_digits:
        return False
    
    return True

def check_number(register_number):
    validity = is_valid_number(register_number)
    if validity != True:
        if validity == False:
            return "invalid register number - check digits"
        else:
            return f"invalid register number - {validity}"

    numbers_only = register_number.replace(".","").replace("-","")
    birth_part = numbers_only[:6]
    sequence_part = int(numbers_only[6:9])
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

    if 1 <= sequence_part <= 100:
        return f"valid register number (early) - {generation}"
    elif 900 <= sequence_part <= 999:
        return f"valid register number (late) - {generation}"
    else:
        return f"valid register number - {generation}"

def structured_info(register_number):
    numbers_only = register_number.replace(".", "").replace("-", "")
    birth_part = numbers_only[:6]
    sequence_part = int(numbers_only[6:9])
    year_prefix = 2000 if int(numbers_only[0]) in [0, 1] else 1900
    birth_year = year_prefix + int(birth_part[:2])
    birth_month = int(birth_part[2:4])
    birth_day = int(birth_part[4:6])
    birth_date = datetime.date(birth_year, birth_month, birth_day)
    today = datetime.date.today()
    age = today.year - birth_year - ((today.month, today.day) < (birth_month, birth_day))
    gender = "Male" if sequence_part % 2 != 0 else "Female"
    generation = check_number(register_number).split("-")[-1].strip()

    table = [["Date of Birth", birth_date.strftime("%B %d, %Y")],["Gender", gender],["Age", age],["Generation", generation]]
    print(tabulate(table, tablefmt="grid"))

def generate_qr(register_number):
    img = qrcode.make(register_number)
    img.save(f"{register_number}.png")
    print("image saved")

def get_names(gender, birth_year):
    file_name = "male.txt" if gender.lower() == "male" else "female.txt"
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            names_data = f.readlines()
    except FileNotFoundError:
        return ["Names file not found."]

    for line in names_data:
        year_range, names = line.strip().split("\t")
        start_year, end_year = map(int, year_range.split("-"))
        
        if start_year <= birth_year <= end_year:
            top_names = names.split(", ")[:5]
            return top_names

    return ["Geen namen gevonden voor dit decennium."]

def main():
    register_number = input().strip()
    validity = check_number(register_number)
    print(validity)

    if "invalid" in validity:
        return

    output_type = input().strip().lower()

    if output_type == "table":
        structured_info(register_number)
    elif output_type in ["qr-code", "qr"]:
        generate_qr(register_number)
    elif output_type in ["name", "names"]:
        numbers_only = register_number.replace(".", "").replace("-", "")
        birth_part = numbers_only[:6]
        sequence_part = int(numbers_only[6:9])
        year_prefix = 2000 if int(numbers_only[0]) in [0, 1] else 1900
        birth_year = year_prefix + int(birth_part[:2])
        gender = "Male" if sequence_part % 2 != 0 else "Female"
        top_names = get_names(gender, birth_year)
        print(top_names)
    else:
        print("Invalid output type.")

if __name__ == "__main__":
    main()

# Chaybon Verlooy
# BADI 1 - Scripting