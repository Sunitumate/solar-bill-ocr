import streamlit as st
import pytesseract
from PIL import Image
import re
from openpyxl import Workbook

# =====================================
# TESSERACT PATH
# =====================================
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# =====================================
# PAGE SETTINGS
# =====================================
st.set_page_config(page_title="Solar Bill OCR App")

st.title("⚡ Solar Bill OCR App")
st.markdown("### AI Powered Electricity Bill Reader 🇮🇳")

# =====================================
# FILE UPLOADER
# =====================================
uploaded_file = st.file_uploader(
    "Upload Electricity Bill",
    type=["jpg", "jpeg", "png"]
)

# =====================================
# MAIN PROCESS
# =====================================
if uploaded_file:

    # Open Image
    image = Image.open(uploaded_file)

    # Show Uploaded Image
    st.image(
        image,
        caption="Uploaded Bill",
        use_container_width=True
    )

    # =====================================
    # OCR EXTRACTION
    # =====================================
    try:

        text = pytesseract.image_to_string(image)

    except Exception:

        st.error("OCR Failed")
        st.stop()

    # =====================================
    # SHOW OCR TEXT
    # =====================================
    st.subheader("📄 Extracted Text")

    st.text(text)

    # =====================================
    # CLEAN TEXT
    # =====================================
    clean_text = text.upper()

    # =====================================
    # CUSTOMER NAME
    # =====================================
    customer_name = "Not Found"

    lines = clean_text.split("\n")

    for line in lines:

        line = line.strip()

        # Skip short lines
        if len(line) < 6:
            continue

        # Remove unwanted words
        invalid_words = [

            "BILL",
            "SUPPLY",
            "MONTH",
            "AMOUNT",
            "TOTAL",
            "MSEDCL",
            "MAHAVITARAN",
            "TAX",
            "CONSUMER",
            "ELECTRICITY",
            "PAYMENT",
            "ACCOUNT",
            "NUMBER",
            "ENERGY",
            "POWER",
            "LIMITED",
            "DOWNLOAD",
            "ONLINE"

        ]

        if any(word in line for word in invalid_words):
            continue

        # Detect proper names
        if re.fullmatch(r'[A-Z ]{6,}', line):

            words = line.split()

            # Name should have 2 to 4 words
            if 2 <= len(words) <= 4:

                customer_name = line
                break

    # =====================================
    # BILL AMOUNT
    # =====================================
    bill_amount = "Not Found"

    amounts = re.findall(
        r'\d+\.\d{2}',
        clean_text
    )

    valid_amounts = []

    for amt in amounts:

        value = float(amt)

        if 50 <= value <= 100000:

            valid_amounts.append(value)

    if valid_amounts:

        bill_amount = str(max(valid_amounts))

    # =====================================
    # UNITS
    # =====================================
    units = "Not Found"

    unit_patterns = [

        r'UNITS[:\-]?\s*(\d+)',

        r'CONSUMPTION[:\-]?\s*(\d+)',

        r'KWH[:\-]?\s*(\d+)',

        r'CURRENT READING[:\-]?\s*(\d+)'
    ]

    for pattern in unit_patterns:

        match = re.search(pattern, clean_text)

        if match:

            value = int(match.group(1))

            if 1 <= value <= 100000:

                units = str(value)
                break

    # =====================================
    # BILL NUMBER
    # =====================================
    bill_number = "Not Found"

    bill_patterns = [

        r'BILL NO[:\-]?\s*(\d+)',

        r'ACCOUNT NO[:\-]?\s*(\d+)',

        r'CONSUMER NO[:\-]?\s*(\d+)'
    ]

    for pattern in bill_patterns:

        match = re.search(pattern, clean_text)

        if match:

            bill_number = match.group(1)
            break

    # =====================================
    # FINAL OUTPUT
    # =====================================
    st.subheader("📊 Important Extracted Data")

    st.success(f"👤 Customer Name: {customer_name}")

    st.info(f"💰 Bill Amount: ₹ {bill_amount}")

    st.warning(f"⚡ Units: {units}")

    st.write(f"🧾 Bill Number: {bill_number}")

    st.success("Bill Processed Successfully ✅")

    # =====================================
    # CREATE EXCEL FILE
    # =====================================
    workbook = Workbook()

    sheet = workbook.active

    sheet["A1"] = "Customer Name"
    sheet["B1"] = customer_name

    sheet["A2"] = "Bill Amount"
    sheet["B2"] = bill_amount

    sheet["A3"] = "Units"
    sheet["B3"] = units

    sheet["A4"] = "Bill Number"
    sheet["B4"] = bill_number

    output_file = "bill_output.xlsx"

    workbook.save(output_file)

    # =====================================
    # DOWNLOAD BUTTON
    # =====================================
    with open(output_file, "rb") as file:

        st.download_button(
            label="📥 Download Excel File",
            data=file,
            file_name=output_file,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
