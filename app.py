import streamlit as st
import easyocr
import cv2
import numpy as np
import pandas as pd
import re
from PIL import Image

# -----------------------------
# Streamlit Config
# -----------------------------
st.set_page_config(
    page_title="⚡ Smart Bill OCR",
    layout="wide"
)

st.title("⚡ Smart Electricity Bill OCR")
st.write("Upload any electricity bill image and extract details automatically.")

# -----------------------------
# Upload File
# -----------------------------
uploaded_file = st.file_uploader(
    "Upload Bill Image",
    type=["jpg", "jpeg", "png"]
)

# -----------------------------
# Image Preprocessing
# -----------------------------
def preprocess_image(image):

    img = np.array(image.convert("RGB"))

    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    thresh = cv2.threshold(
        blur,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    return thresh

# -----------------------------
# OCR Extraction
# -----------------------------
@st.cache_resource
def load_reader():
    return easyocr.Reader(['en'], gpu=False)

def extract_text(image):

    reader = load_reader()

    results = reader.readtext(image, detail=0)

    text = "\n".join(results)

    return text

# -----------------------------
# Smart Data Extraction
# -----------------------------
def extract_fields(text):

    data = {
        "Customer Name": "Not Found",
        "Bill Number": "Not Found",
        "Bill Amount": "Not Found",
        "Units": "Not Found",
        "Bill Date": "Not Found"
    }

    # -----------------------------
    # Bill Number
    # -----------------------------
    bill_patterns = [
        r'Consumer\s*No\.?\s*[:\-]?\s*(\d+)',
        r'Bill\s*No\.?\s*[:\-]?\s*(\d+)',
        r'Customer\s*No\.?\s*[:\-]?\s*(\d+)',
        r'(\d{10,16})'
    ]

    for pattern in bill_patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            data["Bill Number"] = match.group(1)
            break

    # -----------------------------
    # Bill Amount
    # -----------------------------
    amount_patterns = [
        r'Amount\s*Payable\s*[:\-]?\s*(\d+\.?\d*)',
        r'Current\s*Bill\s*[:\-]?\s*(\d+\.?\d*)',
        r'Bill\s*Amount\s*[:\-]?\s*(\d+\.?\d*)',
        r'Net\s*Amount\s*[:\-]?\s*(\d+\.?\d*)',
        r'Rs\.?\s*(\d+\.?\d*)'
    ]

    for pattern in amount_patterns:

        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            data["Bill Amount"] = match.group(1)
            break

    # Fallback Amount
    if data["Bill Amount"] == "Not Found":

        amounts = re.findall(r'\d+\.\d{2}', text)

        if amounts:
            data["Bill Amount"] = max(amounts)

    # -----------------------------
    # Units
    # -----------------------------
    unit_patterns = [
        r'Units\s*[:\-]?\s*(\d+)',
        r'Consumption\s*[:\-]?\s*(\d+)',
        r'Current\s*Reading\s*[:\-]?\s*(\d+)',
        r'Unit\s*Consumed\s*[:\-]?\s*(\d+)'
    ]

    for pattern in unit_patterns:

        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            data["Units"] = match.group(1)
            break

    # -----------------------------
    # Bill Date
    # -----------------------------
    date_match = re.search(
        r'\d{2}[/-]\d{2}[/-]\d{4}',
        text
    )

    if date_match:
        data["Bill Date"] = date_match.group()

    # -----------------------------
    # Customer Name
    # -----------------------------
    lines = text.split("\n")

    for line in lines:

        clean_line = line.strip()

        if len(clean_line) > 5:

            if clean_line.isupper():

                blocked_words = [
                    'bill',
                    'amount',
                    'units',
                    'consumer',
                    'number',
                    'date'
                ]

                if not any(word in clean_line.lower() for word in blocked_words):

                    data["Customer Name"] = clean_line
                    break

    return data

# -----------------------------
# Main Logic
# -----------------------------
if uploaded_file:

    image = Image.open(uploaded_file)

    st.image(
        image,
        caption="Uploaded Bill",
        use_container_width=True
    )

    with st.spinner("Processing Bill..."):

        processed_image = preprocess_image(image)

        extracted_text = extract_text(processed_image)

        extracted_data = extract_fields(extracted_text)

    st.success("Bill Processed Successfully ✅")

    col1, col2 = st.columns(2)

    with col1:

        st.info(f"👤 Customer Name: {extracted_data['Customer Name']}")

        st.success(f"💰 Bill Amount: ₹ {extracted_data['Bill Amount']}")

        st.warning(f"⚡ Units: {extracted_data['Units']}")

    with col2:

        st.info(f"🧾 Bill Number: {extracted_data['Bill Number']}")

        st.success(f"📅 Bill Date: {extracted_data['Bill Date']}")

    # -----------------------------
    # Excel Export
    # -----------------------------
    df = pd.DataFrame([extracted_data])

    excel_file = "bill_data.xlsx"

    df.to_excel(excel_file, index=False)

    with open(excel_file, "rb") as file:

        st.download_button(
            label="📥 Download Excel",
            data=file,
            file_name="bill_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # -----------------------------
    # OCR Text
    # -----------------------------
    with st.expander("📄 View OCR Extracted Text"):

        st.text(extracted_text)
