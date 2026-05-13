import streamlit as st
import pytesseract
from PIL import Image
import re
from openpyxl import Workbook

# =====================================
# TESSERACT PATH (STREAMLIT CLOUD)
# =====================================
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# =====================================
# PAGE CONFIG
# =====================================
st.set_page_config(page_title="Solar Bill OCR", layout="centered")

st.title("⚡ Solar Bill OCR App")
st.markdown("### AI Powered Electricity Bill Reader ⚡")

# =====================================
# FILE UPLOAD
# =====================================
uploaded_file = st.file_uploader(
    "Upload Electricity Bill",
    type=["jpg", "jpeg", "png"]
)

# =====================================
# PROCESS IMAGE
# =====================================
if uploaded_file:

    image = Image.open(uploaded_file)

    st.image(
        image,
        caption="Uploaded Bill",
        use_container_width=True
    )

    # =====================================
    # OCR
    # =====================================
    try:
        text = pytesseract.image_to_string(image)

    except Exception as e:
        st.error("OCR failed")
        st.stop()

    # =====================================
    # SHOW OCR TEXT
    # =====================================
    st.subheader("📄 Extracted Text")
    st.text(text)

    # =====================================
    # CLEAN TEXT
    # =====================================
    clean_text = text.replace("\n", " ").upper()

    # =====================================
    # CUSTOMER NAME EXTRACTION
    # =====================================
    name = "Not Found"

    name_patterns = [
        r'NAME[:\-]?\s*([A-Z ]{5,40})',
        r'CONSUMER NAME[:\-]?\s*([A-Z ]{5,40})',
        r'CUSTOMER NAME[:\-]?\s*([A-Z ]{5,40})'
    ]

    for pattern in name_patterns:
        match = re.search(pattern, clean_text)

        if match:
            name = match.group(1).strip()
            break

    # =====================================
    # BILL AMOUNT EXTRACTION
    # =====================================
    bill_value = "Not Found"

    amount_patterns = [
        r'RS\.?\s?(\d+\.\d{2})',
        r'AMOUNT[:\-]?\s?(\d+\.\d{2})',
        r'TOTAL[:\-]?\s?(\d+\.\d{2})',
        r'NET AMOUNT[:\-]?\s?(\d+\.\d{2})'
    ]

    for pattern in amount_patterns:

        match = re.search(pattern, clean_text)

        if match:
            bill_value = match.group(1)
            break

    # Fallback Amount Detection
    if bill_value == "Not Found":

        amounts = re.findall(r'\d+\.\d{2}', clean_text)

        filtered_amounts = []

        for amt in amounts:

            value = float(amt)

            if 50 <= value <= 50000:
                filtered_amounts.append(value)

        if filtered_amounts:
            bill_value = str(max(filtered_amounts))

    # =====================================
    # UNITS EXTRACTION
    # =====================================
    units_value = "Not Found"

    units_patterns = [
        r'UNITS[:\-]?\s?(\d+)',
        r'CONSUMPTION[:\-]?\s?(\d+)',
        r'KWH[:\-]?\s?(\d+)'
    ]

    for pattern in units_patterns:

        match = re.search(pattern, clean_text)

        if match:
            units_value = match.group(1)
            break

    # Fallback Units Detection
    if units_value == "Not Found":

        numbers = re.findall(r'\b\d+\b', clean_text)

        valid_units = []

        for num in numbers:

            value = int(num)

            if 50 <= value <= 5000:
                valid_units.append(value)

        if valid_units:
            units_value = str(valid_units[0])

    # =====================================
    # DISPLAY OUTPUT
    # =====================================
    st.subheader("📊 Important Extracted Data")

    st.success(f"👤 Customer Name: {name}")

    st.info(f"💰 Bill Amount: {bill_value}")

    st.warning(f"⚡ Units: {units_value}")

    st.success("Bill Processed Successfully ✅")

    # =====================================
    # CREATE EXCEL FILE
    # =====================================
    workbook = Workbook()

    sheet = workbook.active

    sheet["A1"] = "Customer Name"
    sheet["B1"] = name

    sheet["A2"] = "Bill Amount"
    sheet["B2"] = bill_value

    sheet["A3"] = "Units"
    sheet["B3"] = units_value

    file_name = "solar_bill_output.xlsx"

    workbook.save(file_name)

    # =====================================
    # DOWNLOAD BUTTON
    # =====================================
    with open(file_name, "rb") as file:

        st.download_button(
            label="📥 Download Excel Report",
            data=file,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
