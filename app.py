def extract_fields(text):

    data = {
        "Customer Name": "Not Found",
        "Bill Amount": "Not Found",
        "Units": "Not Found",
        "Bill Number": "Not Found",
        "Bill Date": "Not Found"
    }

    # -----------------------------
    # BILL NUMBER
    # -----------------------------
    bill_patterns = [
        r'Consumer\s*No\.?\s*[:\-]?\s*(\d+)',
        r'Customer\s*No\.?\s*[:\-]?\s*(\d+)',
        r'Account\s*No\.?\s*[:\-]?\s*(\d+)',
        r'Bill\s*No\.?\s*[:\-]?\s*(\d+)',
        r'CA\s*No\.?\s*[:\-]?\s*(\d+)',
        r'(\d{10,16})'
    ]

    for pattern in bill_patterns:

        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            data["Bill Number"] = match.group(1)
            break

    # -----------------------------
    # BILL AMOUNT
    # -----------------------------
    amount_patterns = [

        r'Amount\s*Payable\s*[:\-]?\s*Rs\.?\s*(\d+\.?\d*)',

        r'Net\s*Amount\s*[:\-]?\s*Rs\.?\s*(\d+\.?\d*)',

        r'Current\s*Bill\s*[:\-]?\s*Rs\.?\s*(\d+\.?\d*)',

        r'Total\s*Amount\s*[:\-]?\s*Rs\.?\s*(\d+\.?\d*)',

        r'Bill\s*Amount\s*[:\-]?\s*Rs\.?\s*(\d+\.?\d*)',

        r'Rs\.?\s*(\d+\.\d{2})'
    ]

    for pattern in amount_patterns:

        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            data["Bill Amount"] = match.group(1)
            break

    # -----------------------------
    # UNITS
    # -----------------------------
    unit_patterns = [

        r'Units\s*Consumed\s*[:\-]?\s*(\d+)',

        r'Consumption\s*[:\-]?\s*(\d+)',

        r'Current\s*Reading\s*[:\-]?\s*(\d+)',

        r'Units\s*[:\-]?\s*(\d+)',

        r'Unit\s*Consumed\s*[:\-]?\s*(\d+)'
    ]

    for pattern in unit_patterns:

        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            data["Units"] = match.group(1)
            break

    # -----------------------------
    # DATE
    # -----------------------------
    date_patterns = [

        r'\d{2}[/-]\d{2}[/-]\d{4}',

        r'\d{2}-[A-Za-z]{3}-\d{4}',

        r'\d{2}\.\d{2}\.\d{2024}'
    ]

    for pattern in date_patterns:

        match = re.search(pattern, text)

        if match:
            data["Bill Date"] = match.group()
            break

    # -----------------------------
    # CUSTOMER NAME
    # -----------------------------
    lines = text.split("\n")

    blocked_words = [
        'bill',
        'amount',
        'units',
        'consumer',
        'number',
        'date',
        'reading',
        'payment',
        'voltage',
        'tariff'
    ]

    for line in lines:

        clean_line = line.strip()

        if len(clean_line) > 5:

            if any(char.isalpha() for char in clean_line):

                if not any(word in clean_line.lower() for word in blocked_words):

                    if len(clean_line.split()) <= 6:

                        data["Customer Name"] = clean_line
                        break

    return data
