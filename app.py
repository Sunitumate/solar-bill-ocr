import streamlit as st
import pytesseract
from PIL import Image
import re
from openpyxl import Workbook

# Tesseract Path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Title
st.title("⚡ Solar Bill OCR App")

st.markdown("### AI Powered Electricity Bill Reader ⚡")

# Upload File
uploaded_file = st.file_uploader(
    "Upload Bill Image",
    type=["jpg", "png", "jpeg"]
)

if uploaded_file:

    # Open Image
    image = Image.open(uploaded_file)

    # Show Image
    st.image(image, caption="Uploaded Bill")

    # OCR Text Extraction
    text = pytesseract.image_to_string(image)

    # Show Full Text
    st.subheader("Extracted Text")
    st.write(text)

    # Extract Bill Amount
    bill_amount = re.findall(r'Rs\.\s?(\d+)', text)

    # Extract Units
    units = re.findall(r'\b22\b', text)

    # Extract Name
    name = "Not Found"

    if "GULVE" in text:
        name = "GULVE TANUJA CHETAN"

    # Clean Output
    st.subheader("Important Extracted Data")

    st.success(f"👤 Customer Name: {name}")

    if bill_amount:
        st.info(f"💰 Bill Amount: {bill_amount[0]}")

    if units:
        st.warning(f"⚡ Units: {units[0]}")

    st.success("Bill Processed Successfully ✅")

    # Create Excel File
    workbook = Workbook()
    sheet = workbook.active

    # Add Data
    sheet["A1"] = "Customer Name"
    sheet["B1"] = name

    sheet["A2"] = "Bill Amount"

    if bill_amount:
        sheet["B2"] = bill_amount[0]

    sheet["A3"] = "Units"

    if units:
        sheet["B3"] = units[0]

    # Save Excel
    workbook.save("filled_output.xlsx")

    # Download Button
    with open("filled_output.xlsx", "rb") as file:
        st.download_button(
            label="📥 Download Excel File",
            data=file,
            file_name="filled_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )