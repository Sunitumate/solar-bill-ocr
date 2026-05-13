import streamlit as st
import pytesseract
from PIL import Image
import re
from openpyxl import Workbook

# =========================
# STREAMLIT PAGE
# =========================

st.set_page_config(page_title="Solar Bill OCR", layout="centered")

st.title("⚡ Solar Bill OCR App")
st.markdown("### AI Powered Electricity Bill Reader")

# =========================
# FILE UPLOAD
# =========================

uploaded_file = st.file_uploader(
    "Upload Electricity Bill",
    type=["jpg", "jpeg", "png"]
)

# =========================
# PROCESS IMAGE
# =========================

if uploaded_file:

    image = Image.open(uploaded_file)

    st.image(image, caption="Uploaded Bill", use_container_width=True)

    # OCR
    text = pytesseract.image_to_string(image)

    # Show OCR Text
    st.subheader("📄 Extracted Text")
    st.text(text)

    # =========================
    # EXTRACT BILL AMOUNT
    # =========================

    amount_patterns = [
        r'Rs\.?\s?(\d+\.\d+)',
        r'Rs\.?\s?(\d+)',
        r'(\d+\.\d+)\s?Rs',
    ]

    bill_amount = "Not Found"

    for pattern in amount_patterns:

        matches = re.findall(pattern, text)

        if matches:

            values = []

            for m in matches:
                try:
                    values.append(float(m))
                except:
                    pass

            if values:
                bill_amount = max(values)
                break

    # =========================
    # EXTRACT UNITS
    # =========================

    units = "Not Found"

    unit_patterns = [
        r'Units?\s*[:\-]?\s*(\d+)',
        r'Consumption\s*[:\-]?\s*(\d+)',
        r'\b(\d{1,4})\b'
    ]

    for pattern in unit_patterns:

        matches = re.findall(pattern, text, re.IGNORECASE)

        for match in matches:

            value = int(match)

            if 1 <= value <= 5000:
                units = value
                break

        if units != "Not Found":
            break

    # =========================
    # EXTRACT BILL NUMBER
    # =========================

    bill_number = "Not Found"

    bill_patterns = [
        r'Consumer\s*No\.?\s*[:\-]?\s*(\d+)',
        r'Bill\s*No\.?\s*[:\-]?\s*(\d+)',
        r'(\d{12})'
    ]

    for pattern in bill_patterns:

        matches = re.findall(pattern, text, re.IGNORECASE)

        if matches:
            bill_number = matches[0]
            break

    # =========================
    # EXTRACT CUSTOMER NAME
    # =========================

    name = "Not Found"

    lines = text.split("\n")

    for line in lines:

        line = line.strip()

        if len(line) < 5:
            continue

        skip_words = [
            "BILL",
            "SUPPLY",
            "MONTH",
            "GSTIN",
            "Rs",
            "Ray",
            "SOLAR",
            "APPROVED",
            "SCAN",
            "QR",
            "CGRF",
            "Portal",
            "INDIA",
            "PAYMENT"
        ]

        if any(word.lower() in line.lower() for word in skip_words):
            continue

        words = line.split()

        if len(words) >= 2:

            capital_words = [
                w for w in words
                if w.isalpha() and w.upper() == w
            ]

            if len(capital_words) >= 2:

                name = " ".join(capital_words[:4])
                break

    # =========================
    # SHOW RESULTS
    # =========================

    st.subheader("📊 Important Extracted Data")

    st.success(f"👤 Customer Name: {name}")

    st.info(f"💰 Bill Amount: ₹ {bill_amount}")

    st.warning(f"⚡ Units: {units}")

    st.success(f"🧾 Bill Number: {bill_number}")

    st.success("Bill Processed Successfully ✅")

    # =========================
    # CREATE EXCEL FILE
    # =========================

    workbook = Workbook()

    sheet = workbook.active

    sheet.title = "Bill Data"

    sheet["A1"] = "Customer Name"
    sheet["B1"] = name

    sheet["A2"] = "Bill Amount"
    sheet["B2"] = bill_amount

    sheet["A3"] = "Units"
    sheet["B3"] = units

    sheet["A4"] = "Bill Number"
    sheet["B4"] = bill_number

    excel_file = "solar_bill_output.xlsx"

    workbook.save(excel_file)

    # =========================
    # DOWNLOAD BUTTON
    # =========================

    with open(excel_file, "rb") as file:

        st.download_button(
            label="📥 Download Excel File",
            data=file,
            file_name="solar_bill_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
