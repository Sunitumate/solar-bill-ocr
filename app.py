import streamlit as st
import pytesseract
from PIL import Image
import re
from openpyxl import Workbook

# ======================================
# PAGE CONFIG
# ======================================

st.set_page_config(
    page_title="Solar Bill OCR App",
    layout="centered"
)

st.title("⚡ Solar Bill OCR App")
st.markdown("### AI Powered Electricity Bill Reader 🇮🇳")

# ======================================
# TESSERACT PATH
# ======================================

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# ======================================
# FILE UPLOAD
# ======================================

uploaded_file = st.file_uploader(
    "Upload Electricity Bill",
    type=["jpg", "jpeg", "png"]
)

# ======================================
# PROCESS BILL
# ======================================

if uploaded_file:

    # Open Image
    image = Image.open(uploaded_file)

    # Show Image
    st.image(
        image,
        caption="Uploaded Bill",
        use_container_width=True
    )

    # ======================================
    # OCR TEXT EXTRACTION
    # ======================================

    try:

        text = pytesseract.image_to_string(image)

    except Exception as e:

        st.error("OCR Failed")
        st.write(e)
        st.stop()

    # ======================================
    # SHOW EXTRACTED TEXT
    # ======================================

    st.subheader("📄 Extracted Text")
    st.text(text)

    # ======================================
    # CLEAN OCR TEXT
    # ======================================

    clean_text = text.upper()

    # ======================================
    # CUSTOMER NAME EXTRACTION
    # ======================================

    customer_name = "Not Found"

    name_patterns = [

        r'([A-Z]{3,}\s+[A-Z]{3,}\s+[A-Z]{3,})',

        r'([A-Z]{3,}\s+[A-Z]{3,})'
    ]

    skip_words = [

        "BILL OF SUPPLY",
        "FOR THE MONTH",
        "SOLAR PANELS",
        "TOPCON SOLAR",
        "GSTIN",
        "PAYMENT",
        "CONSUMER",
        "PORTAL",
        "INDIA",
        "APPROVED",
        "CGRF",
        "SCAN",
        "QR CODE",
        "RAY SOLAR"

    ]

    for pattern in name_patterns:

        matches = re.findall(pattern, clean_text)

        for match in matches:

            valid = True

            for skip in skip_words:

                if skip in match:
                    valid = False
                    break

            if valid:

                customer_name = match.strip()
                break

        if customer_name != "Not Found":
            break

    # ======================================
    # BILL AMOUNT EXTRACTION
    # ======================================

    bill_amount = "Not Found"

    amount_matches = re.findall(
        r'RS\.?\s?(\d+\.\d+)',
        clean_text
    )

    valid_amounts = []

    for amt in amount_matches:

        try:

            value = float(amt)

            if 50 <= value <= 50000:
                valid_amounts.append(value)

        except:
            pass

    if valid_amounts:

        bill_amount = min(valid_amounts)

    # ======================================
    # UNITS EXTRACTION
    # ======================================

    units = "Not Found"

    unit_patterns = [

        r'UNITS?\s*[:\-]?\s*(\d+)',

        r'CONSUMPTION\s*[:\-]?\s*(\d+)'
    ]

    for pattern in unit_patterns:

        match = re.search(pattern, clean_text)

        if match:

            units = match.group(1)
            break

    # ======================================
    # BILL NUMBER EXTRACTION
    # ======================================

    bill_number = "Not Found"

    bill_match = re.search(
        r'\b\d{12}\b',
        clean_text
    )

    if bill_match:

        bill_number = bill_match.group()

    # ======================================
    # FINAL OUTPUT
    # ======================================

    st.subheader("📊 Important Extracted Data")

    st.success(f"👤 Customer Name: {customer_name}")

    st.info(f"💰 Bill Amount: ₹ {bill_amount}")

    st.warning(f"⚡ Units: {units}")

    st.success(f"🧾 Bill Number: {bill_number}")

    st.success("Bill Processed Successfully ✅")

    # ======================================
    # CREATE EXCEL FILE
    # ======================================

    workbook = Workbook()

    sheet = workbook.active

    sheet.title = "Bill Data"

    sheet["A1"] = "Customer Name"
    sheet["B1"] = customer_name

    sheet["A2"] = "Bill Amount"
    sheet["B2"] = bill_amount

    sheet["A3"] = "Units"
    sheet["B3"] = units

    sheet["A4"] = "Bill Number"
    sheet["B4"] = bill_number

    output_file = "solar_bill_output.xlsx"

    workbook.save(output_file)

    # ======================================
    # DOWNLOAD BUTTON
    # ======================================

    with open(output_file, "rb") as file:

        st.download_button(
            label="📥 Download Excel File",
            data=file,
            file_name="solar_bill_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
