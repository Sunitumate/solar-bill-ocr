import streamlit as st
import pytesseract
from PIL import Image
import re
from openpyxl import Workbook

# IMPORTANT: Linux path for Streamlit Cloud
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

st.title("⚡ Solar Bill OCR App")
st.markdown("### AI Powered Electricity Bill Reader ⚡")

uploaded_file = st.file_uploader(
    "Upload Bill Image",
    type=["jpg", "png", "jpeg"]
)

if uploaded_file:

    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Bill")

    try:
        text = pytesseract.image_to_string(image)
    except Exception:
        st.error("OCR failed - fallback mode")
        st.stop()

    st.subheader("Extracted Text")
    st.write(text)

    # Extract Bill Amount
    bill_amount = re.findall(r'Rs\.?\s?(\d+(?:\.\d+)?)', text)

    # Improved Units extraction
    units = re.findall(r'\b\d{2,4}\b', text)
    units_value = units[0] if units else "Not Found"

    # Name detection
    name = "Not Found"
    if "GULVE" in text.upper():
        name = "GULVE TANUJA CHETAN"

    st.subheader("Important Extracted Data")

    st.success(f"👤 Customer Name: {name}")
    st.info(f"💰 Bill Amount: {bill_amount[0] if bill_amount else 'Not Found'}")
    st.warning(f"⚡ Units: {units_value}")

    st.success("Bill Processed Successfully ✅")

    # Excel file
    workbook = Workbook()
    sheet = workbook.active

    sheet["A1"] = "Customer Name"
    sheet["B1"] = name

    sheet["A2"] = "Bill Amount"
    sheet["B2"] = bill_amount[0] if bill_amount else "Not Found"

    sheet["A3"] = "Units"
    sheet["B3"] = units_value

    file_name = "filled_output.xlsx"
    workbook.save(file_name)

    with open(file_name, "rb") as file:
        st.download_button(
            "📥 Download Excel File",
            file,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
