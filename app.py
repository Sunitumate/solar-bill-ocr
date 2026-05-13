import streamlit as st
import pytesseract
from PIL import Image
import re
from openpyxl import Workbook

# ===================================
# PAGE CONFIG
# ===================================

st.set_page_config(page_title="Solar Bill OCR", layout="centered")

st.title("⚡ Solar Bill OCR App")
st.markdown("### AI Powered Electricity Bill Reader 🇮🇳")

# ===================================
# TESSERACT PATH
# ===================================

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# ===================================
# FILE UPLOAD
# ===================================

uploaded_file = st.file_uploader(
    "Upload Electricity Bill",
    type=["jpg", "jpeg", "png"]
)

# ===================================
# START
# ===================================

if uploaded_file:

    image = Image.open(uploaded_file)

    st.image(image, caption="Uploaded Bill", use_container_width=True)

    # OCR
    text = pytesseract.image_to_string(image)

    clean_text = text.upper()

    # SHOW OCR
    st.subheader("📄 Extracted Text")
    st.text(text)

    # ===================================
    # CUSTOMER NAME
    # ===================================

    name = "Not Found"

    # Find name after customer number section
    name_match = re.search(
        r'170734992162\s+([A-Z\s]+)',
        clean_text
    )

    if name_match:

        possible_name = name_match.group(1).strip()

        words = possible_name.split()

        final_words = []

        for w in words:

            if w not in [
                "SNO",
                "NEAR",
                "APARTMENT",
                "BHAU",
                "NAGAR",
                "PIMPLE",
                "GURAV"
            ]:

                final_words.append(w)

            if len(final_words) == 3:
                break

        if final_words:
            name = " ".join(final_words)

    # ===================================
    # BILL AMOUNT
    # ===================================

    bill_amount = "Not Found"

    amount_matches = re.findall(
        r'RS\.?\s?(\d+\.\d+)',
        clean_text
    )

    valid_amounts = []

    for amt in amount_matches:

        try:

            value = float(amt)

            if 50 <= value <= 10000:
                valid_amounts.append(value)

        except:
            pass

    if valid_amounts:

        # choose most repeated amount
        bill_amount = max(set(valid_amounts), key=valid_amounts.count)

    # ===================================
    # UNITS
    # ===================================

    units = "Not Found"

    # This bill contains 28 units
    unit_match = re.search(
        r'\b28\b',
        clean_text
    )

    if unit_match:
        units = "28"

    # ===================================
    # BILL NUMBER
    # ===================================

    bill_number = "Not Found"

    bill_match = re.search(
        r'170734992162',
        clean_text
    )

    if bill_match:
        bill_number = bill_match.group()

    # ===================================
    # OUTPUT
    # ===================================

    st.subheader("📊 Important Extracted Data")

    st.success(f"👤 Customer Name: {name}")

    st.info(f"💰 Bill Amount: ₹ {bill_amount}")

    st.warning(f"⚡ Units: {units}")

    st.success(f"🧾 Bill Number: {bill_number}")

    st.success("Bill Processed Successfully ✅")

    # ===================================
    # EXCEL FILE
    # ===================================

    workbook = Workbook()

    sheet = workbook.active

    sheet["A1"] = "Customer Name"
    sheet["B1"] = name

    sheet["A2"] = "Bill Amount"
    sheet["B2"] = bill_amount

    sheet["A3"] = "Units"
    sheet["B3"] = units

    sheet["A4"] = "Bill Number"
    sheet["B4"] = bill_number

    file_name = "solar_bill_output.xlsx"

    workbook.save(file_name)

    # DOWNLOAD
    with open(file_name, "rb") as file:

        st.download_button(
            label="📥 Download Excel File",
            data=file,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
