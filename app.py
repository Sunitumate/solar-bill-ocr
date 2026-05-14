import streamlit as st
import easyocr
import cv2
import numpy as np
import pandas as pd
import re
from PIL import Image

st.set_page_config(page_title="Industry Bill OCR", layout="wide")

st.title("⚡ Industry Level Electricity Bill OCR")
st.write("Upload any electricity bill image and extract important details automatically.")

uploaded_file = st.file_uploader(
    "Upload Bill Image",
    type=["jpg", "jpeg", "png"]
)

# -----------------------------
# Image Preprocessing
# -----------------------------
def preprocess_image(image):
    img = np.array(image.convert('RGB'))

    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    thresh = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    return thresh

# -----------------------------
# OCR Extraction
# -----------------------------
def extract_text(image):
    reader = easyocr.Reader(['en'], gpu=False)

    results = reader.readtext(image, detail=0)

    text = "\n".join(results)

    return text

# -----------------------------
# Smart Field Extraction
# -----------------------------
def extract_fields(text):
    data = {
        "Customer Name": "Not Found",
        "Bill Amount": "Not Found",
        "Units": "Not Found",
        "Bill Number": "Not Found",
        "Bill Date": "Not Found"
    }

    # Bill Number
    bill_patterns = [
        r'Consumer No\.?\s*[:\-]?\s*(\d+)',
        r'Bill No\.?\s*[:\-]?\s*(\d+)',
        r'Customer No\.?\s*[:\-]?\s*(\d+)',
        r'(\d{10,16})'
    ]

    for pattern in bill_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data["Bill Number"] = match.group(1)
            break

    # Bill Amount
    amount_patterns = [
        r'Amount\s*Payable\s*[:\-]?\s*(\d+\.?\d*)',
        r'Current\s*Bill\s*[:\-]?\s*(\d+\.?\d*)',
        r'Bill\s*Amount\s*[:\-]?\s*(\d+\.?\d*)',
        r'Rs\.?\s*(\d+\.?\d*)'
    ]

    for pattern in amount_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data["Bill Amount"] = match.group(1)
            break

    # Fallback Amount
    if data["Bill Amount"] == "Not Found":
        all_amounts = re.findall(r'\d+\.\d{2}', text)
        if all_amounts:
            data["Bill Amount"] = max(all_amounts)

    # Units
    unit_patterns = [
        r'Units\s*[:\-]?\s*(\d+)',
        r'Consumption\s*[:\-]?\s*(\d+)',
        r'Unit\s*Consumed\s*[:\-]?\s*(\d+)',
        r'Current\s*Reading\s*[:\-]?\s*(\d+)'
    ]

    for pattern in unit_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data["Units"] = match.group(1)
            break

    # Date
    date_match = re.search(r'\d{2}[/-]\d{2}[/-]\d{4}', text)
    if date_match:
        data["Bill Date"] = date_match.group()

    # Customer Name
    lines = text.split('\n')

    for line in lines:
        clean_line = line.strip()

        if len(clean_line) > 5:
            if clean_line.isupper():
                if not any(word in clean_line.lower() for word in [
                    'bill', 'amount', 'units', 'consumer', 'number', 'date'
                ]):
                    data["Customer Name"] = clean_line
                    break

    return data

# -----------------------------
# Main App
# -----------------------------
if uploaded_file:
    image = Image.open(uploaded_file)

    st.image(image, caption="Uploaded Bill", use_container_width=True)

    with st.spinner("Processing Bill..."):
        processed = preprocess_image(image)

        text = extract_text(processed)

        extracted_data = extract_fields(text)

    st.success("Bill Processed Successfully ✅")

    col1, col2 = st.columns(2)

    with col1:
        st.info(f"👤 Customer Name: {extracted_data['Customer Name']}")
        st.success(f"💰 Bill Amount: ₹ {extracted_data['Bill Amount']}")
        st.warning(f"⚡ Units: {extracted_data['Units']}")

    with col2:
        st.info(f"🧾 Bill Number: {extracted_data['Bill Number']}")
        st.success(f"📅 Bill Date: {extracted_data['Bill Date']}")

    # Export Excel
    df = pd.DataFrame([extracted_data])

    excel_file = "bill_data.xlsx"

    df.to_excel(excel_file, index=False)

    with open(excel_file, "rb") as file:
        st.download_button(
            label="📥 Download Excel File",
            data=file,
            file_name="bill_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with st.expander("View OCR Extracted Text"):
        st.text(text)
