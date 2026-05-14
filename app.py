import streamlit as st
import pytesseract
from PIL import Image
import pandas as pd
import re

st.title("⚡ Simple Bill OCR")

uploaded_file = st.file_uploader(
    "Upload Bill Image",
    type=["jpg", "jpeg", "png"]
)

def extract_fields(text):

    data = {
        "Customer Name": "Not Found",
        "Bill Amount": "Not Found",
        "Units": "Not Found"
    }

    # Amount
    amount = re.search(r'Rs\.?\s*(\d+)', text)

    if amount:
        data["Bill Amount"] = amount.group(1)

    # Units
    units = re.search(r'Units\s*(\d+)', text)

    if units:
        data["Units"] = units.group(1)

    # Name
    lines = text.split("\n")

    for line in lines:

        line = line.strip()

        if len(line) > 5:

            if any(c.isalpha() for c in line):

                data["Customer Name"] = line
                break

    return data

if uploaded_file:

    image = Image.open(uploaded_file)

    st.image(image)

    text = pytesseract.image_to_string(image)

    st.subheader("OCR Text")

    st.text(text)

    data = extract_fields(text)

    st.subheader("Extracted Data")

    st.write("👤 Customer Name:", data["Customer Name"])

    st.write("💰 Bill Amount:", data["Bill Amount"])

    st.write("⚡ Units:", data["Units"])

    df = pd.DataFrame([data])

    st.download_button(
        "Download Excel",
        df.to_csv(index=False),
        "bill_data.csv"
    )
