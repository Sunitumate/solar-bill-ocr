import streamlit as st
import pytesseract
from PIL import Image, ImageFilter
import re
from openpyxl import Workbook

# ==========================================
# TESSERACT PATH FOR STREAMLIT CLOUD
# ==========================================
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# ==========================================
# PAGE SETTINGS
# ==========================================
st.set_page_config(
    page_title="Indian Electricity Bill OCR",
    layout="centered"
)

st.title("⚡ Indian Electricity Bill OCR App")
st.markdown("### AI Powered Bill Reader 🇮🇳")

# ==========================================
# FILE UPLOADER
# ==========================================
uploaded_file = st.file_uploader(
    "Upload Electricity Bill",
    type=["jpg", "jpeg", "png"]
)

# ==========================================
# START PROCESS
# ==========================================
if uploaded_file:

    # Open image
    image = Image.open(uploaded_file)

    # Display image
    st.image(
        image,
        caption="Uploaded Bill",
        use_container_width=True
    )

    # ==========================================
    # IMAGE PREPROCESSING
    # ==========================================
    gray_image = image.convert("L")

    sharpen_image = gray_image.filter(
        ImageFilter.SHARPEN
    )

    # ==========================================
    # OCR
    # ==========================================
    try:

        text = pytesseract.image_to_string(
            sharpen_image
        )

    except Exception:

        st.error("OCR Failed")
        st.stop()

    # ==========================================
    # SHOW OCR TEXT
    # ==========================================
    st.subheader("📄 Extracted Text")

    st.text(text)

    # ==========================================
    # CLEAN TEXT
    # ==========================================
    clean_text = text.replace("\n", " ").upper()

    # ==========================================
    # CUSTOMER NAME
    # ==========================================
    customer_name = "Not Found"

    name_patterns = [

        r'CONSUMER NAME[:\-]?\s*([A-Z ]{5,40})',

        r'CUSTOMER NAME[:\-]?\s*([A-Z ]{5,40})',

        r'NAME[:\-]?\s*([A-Z ]{5,40})'
    ]

    for pattern in name_patterns:

        match = re.search(pattern, clean_text)

        if match:

            extracted_name = match.group(1).strip()

            if len(extracted_name) > 5:

                customer_name = extracted_name
                break

    # ==========================================
    # FALLBACK NAME DETECTION
    # ==========================================
    if customer_name == "Not Found":

        possible_names = re.findall(
            r'[A-Z]{3,}\s[A-Z]{3,}\s?[A-Z]*',
            clean_text
        )

        if possible_names:

            customer_name = possible_names[0]

    # ==========================================
    # BILL AMOUNT
    # ==========================================
    bill_amount = "Not Found"

    amount_patterns = [

        r'RS\.?\s?(\d+\.\d{2})',

        r'AMOUNT[:\-]?\s?(\d+\.\d{2})',

        r'TOTAL[:\-]?\s?(\d+\.\d{2})',

        r'NET AMOUNT[:\-]?\s?(\d+\.\d{2})',

        r'BILL AMOUNT[:\-]?\s?(\d+\.\d{2})'
    ]

    for pattern in amount_patterns:

        match = re.search(pattern, clean_text)

        if match:

            value = float(match.group(1))

            if 50 <= value <= 100000:

                bill_amount = str(value)
                break

    # ==========================================
    # FALLBACK BILL AMOUNT
    # ==========================================
    if bill_amount == "Not Found":

        all_amounts = re.findall(
            r'\d+\.\d{2}',
            clean_text
        )

        valid_amounts = []

        for amt in all_amounts:

            value = float(amt)

            if 50 <= value <= 100000:

                valid_amounts.append(value)

        if valid_amounts:

            bill_amount = str(max(valid_amounts))

    # ==========================================
    # ELECTRICITY UNITS
    # ==========================================
    units = "Not Found"

    unit_patterns = [

        r'UNITS[:\-]?\s?(\d+)',

        r'CONSUMPTION[:\-]?\s?(\d+)',

        r'KWH[:\-]?\s?(\d+)',

        r'CURRENT READING[:\-]?\s?(\d+)'
    ]

    for pattern in unit_patterns:

        match = re.search(pattern, clean_text)

        if match:

            value = int(match.group(1))

            if 1 <= value <= 10000:

                units = str(value)
                break

    # ==========================================
    # FALLBACK UNITS
    # ==========================================
    if units == "Not Found":

        all_numbers = re.findall(
            r'\b\d+\b',
            clean_text
        )

        valid_units = []

        for num in all_numbers:

            value = int(num)

            if 50 <= value <= 5000:

                valid_units.append(value)

        if valid_units:

            units = str(valid_units[0])

    # ==========================================
    # BILL NUMBER
    # ==========================================
    bill_number = "Not Found"

    bill_patterns = [

        r'BILL NO[:\-]?\s?(\d+)',

        r'BILL NUMBER[:\-]?\s?(\d+)',

        r'ACCOUNT NO[:\-]?\s?(\d+)'
    ]

    for pattern in bill_patterns:

        match = re.search(pattern, clean_text)

        if match:

            bill_number = match.group(1)
            break

    # ==========================================
    # SHOW OUTPUT
    # ==========================================
    st.subheader("📊 Important Extracted Data")

    st.success(f"👤 Customer Name: {customer_name}")

    st.info(f"💰 Bill Amount: {bill_amount}")

    st.warning(f"⚡ Units: {units}")

    st.write(f"🧾 Bill Number: {bill_number}")

    st.success("Bill Processed Successfully ✅")

    # ==========================================
    # EXCEL EXPORT
    # ==========================================
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

    output_file = "indian_bill_output.xlsx"

    workbook.save(output_file)

    # ==========================================
    # DOWNLOAD BUTTON
    # ==========================================
    with open(output_file, "rb") as file:

        st.download_button(
            label="📥 Download Excel Report",
            data=file,
            file_name=output_file,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
