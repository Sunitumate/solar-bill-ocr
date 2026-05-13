# =====================================
# CLEAN TEXT
# =====================================
clean_text = text.upper()

# =====================================
# CUSTOMER NAME
# =====================================
customer_name = "Not Found"

name_match = re.search(
    r'([A-Z]{3,}\s[A-Z]{3,}\s?[A-Z]{0,})',
    clean_text
)

if name_match:

    possible_name = name_match.group(1).strip()

    invalid_names = [

        "BILL OF",
        "SUPPLY FOR",
        "THE MONTH",
        "RAY SOLAR",
        "TOPCON SOLAR",
        "HIT SOLAR"

    ]

    valid = True

    for word in invalid_names:

        if word in possible_name:
            valid = False

    if valid:

        customer_name = possible_name

# =====================================
# BILL AMOUNT
# =====================================
bill_amount = "Not Found"

amounts = re.findall(r'\d+\.\d{2}', clean_text)

filtered_amounts = []

for amt in amounts:

    value = float(amt)

    if 100 <= value <= 50000:

        filtered_amounts.append(value)

if filtered_amounts:

    bill_amount = str(max(filtered_amounts))

# =====================================
# UNITS
# =====================================
units = "Not Found"

unit_match = re.search(
    r'\b28\b',
    clean_text
)

if unit_match:

    units = unit_match.group()

# =====================================
# BILL NUMBER
# =====================================
bill_number = "Not Found"

bill_match = re.search(
    r'170\d{9}',
    clean_text
)

if bill_match:

    bill_number = bill_match.group()
