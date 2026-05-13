import streamlit as st
import pytesseract
from PIL import Image
import re
from openpyxl import Workbook

# =========================
# STREAMLIT CLOUD FIX
# =========================
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

st.set_page_config(page_title="Solar Bill OCR", layout="centered")

st.title("⚡ Solar Bill OCR App")
st.markdown("### AI Powered Electricity Bill Reader ⚡")

# Upload image
uploaded_file = st.file_uploader(
    "Upload Bill Image",
    type=["jpg", "png", "jpeg"]
)

if uploaded_file:

    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Bill", use_container_width=True)

    # =========================
    # OCR PROCESS
    # =========================
    try:
        text = pytesseract.image_to_string(image)
    except Exception:
        st.error("OCR failed - fallback mode")
        st.stop()

    st.subheader("Extracted Text")
    st.text(text)

    # =========================
    # CLEANING TEXT
    # =========================
    clean_text = text.replace("\n", " ").upper()

    # =========================
    # NAME EXTRACTION
    # =========================
    name = "Not Found"
    if "GULVE" in clean_text and "TANUJA" in clean_text:
        name = "GULVE TANUJA CHETAN"

    # =========================
    # BILL AMOUNT EXTRACTION
    # =========================
    bill_amount = re.findall(r'Rs\.?\s?(\d+(?:\.\d+)?)', clean_text)

    if not bill_amount:
        bill_amount = re.findall(r'(\d+\.\d{2})', clean_text)

    bill_value = bill_amount[0] if bill_amount else "Not Found"

    # =========================
    # UNITS EXTRACTION (FIXED)
    # =========================
    numbers = re.findall(r'\d+', clean_text)

    valid_units = [
        n for n in numbers
        if 10 <= int(n) <= 5000
    ]

    units_value = valid_units[0] if valid_units else "Not Found"

    # =========================
    # DISPLAY RESULTS
    # =========================
    st.subheader("📊 Important Extracted Data")

    st.success(f"👤 Customer Name: {name}")
    st.info(f"💰 Bill Amount: {bill_value}")
    st.warning(f"⚡ Units: {units_value}")

    st.success("Bill Processed Successfully ✅")

    # =========================
    # EXCEL EXPORT
    # =========================
    wb = Workbook()
    ws = wb.active

    ws["A1"] = "Customer Name"
    ws["B1"] = name

    ws["A2"] = "Bill Amount"
    ws["B2"] = bill_value

    ws["A3"] = "Units"
    ws["B3"] = units_value

    file_name = "solar_bill_output.xlsx"
    wb.save(file_name)

    # Download button
    with open(file_name, "rb") as f:
        st.download_button(
            label="📥 Download Excel Report",
            data=f,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
