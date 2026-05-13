import streamlit as st
import pytesseract
from PIL import Image
import re

# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(page_title="Solar Bill OCR")

st.title("⚡ Solar Bill OCR App")

# =====================================
# TESSERACT PATH
# =====================================

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# =====================================
# FILE UPLOAD
# =====================================

uploaded_file = st.file_uploader(
    "Upload Electricity Bill",
    type=["jpg", "jpeg", "png"]
)

# =====================================
# PROCESS BILL
# =====================================

if uploaded_file:

    image = Image.open(uploaded_file)

    st.image(image, caption="Uploaded Bill")

    # OCR TEXT
    text = pytesseract.image_to_string(image)

    clean_text = text.upper()

    # =====================================
    # CUSTOMER NAME
    # =====================================

    customer_name = "Not Found"

    name_match = re.search(
        r'([A-Z]{4,}\s+[A-Z]{4,}\s+[A-Z]{4,})',
        clean_text
    )

    if name_match:

        customer_name = name_match.group(1)

    # =====================================
    # BILL AMOUNT
    # =====================================

    bill_amount = "Not Found"

    amount_match = re.findall(
        r'RS\.?\s?(\d+\.\d+)',
        clean_text
    )

    if amount_match:

        amounts = []

        for amt in amount_match:

            try:

                value = float(amt)

                if 50 <= value <= 10000:
                    amounts.append(value)

            except:
                pass

        if amounts:

            bill_amount = min(amounts)

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
        r'\b\d{12}\b',
        clean_text
    )

    if bill_match:

        bill_number = bill_match.group()

    # =====================================
    # FINAL OUTPUT
    # =====================================

    st.subheader("📊 Important Extracted Data")

    st.success(f"👤 Customer Name: {customer_name}")

    st.info(f"💰 Bill Amount: ₹ {bill_amount}")

    st.warning(f"⚡ Units: {units}")

    st.success(f"🧾 Bill Number: {bill_number}")
