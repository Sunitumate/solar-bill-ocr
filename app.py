import streamlit as st
import pytesseract
from PIL import Image
import pandas as pd
import re
import numpy as np

# --- Page Configuration ---
st.set_page_config(page_title="⚡ Solar Bill OCR", layout="centered")

st.title("⚡ Smart Electricity Bill OCR")
st.write("Upload a bill image to automatically extract Customer Name, Amount, and Units.")

# --- File Uploader ---
uploaded_file = st.file_uploader("Upload Bill (JPG, PNG, JPEG)", type=["jpg", "png", "jpeg"])

def extract_info(text):
    """
    Smarter extraction logic to find data even if the bill format changes.
    """
    data = {
        "Customer Name": "Not Found",
        "Bill Amount": "Not Found",
        "Units": "Not Found"
    }

    # 1. Look for Bill Amount (Searches for Rs, Total, Net, or Payable)
    # This pattern handles decimals and commas (e.g., 1,560.00)
    amt_match = re.search(r'(?:Rs|₹|Total|Net|Payable|Amount)[:\s]*([\d,]+\.?\d*)', text, re.IGNORECASE)
    if amt_match:
        data["Bill Amount"] = amt_match.group(1).replace(',', '')

    # 2. Look for Units Consumed (Searches for Units, KWh, or Reading)
    unit_match = re.search(r'(?:Units|Consumed|KWh|Reading|Usage)[:\s]*(\d+)', text, re.IGNORECASE)
    if unit_match:
        data["Units"] = unit_match.group(1)

    # 3. Look for Customer Name
    # We look for a line that has letters and is at least 8 characters long, 
    # skipping lines that contain common "bill words".
    lines = text.split('\n')
    for line in lines:
        clean = line.strip()
        if len(clean) > 8 and any(c.isalpha() for c in clean):
            # Avoid address/utility keywords
            bad_words = ['bill', 'date', 'account', 'consumer', 'limited', 'road', 'street', 'dist', 'tel', 'tax', 'invoice']
            if not any(word in clean.lower() for word in bad_words):
                data["Customer Name"] = clean
                break
                
    return data

if uploaded_file:
    # Open and show the image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Bill Image", use_container_width=True)

    with st.spinner("🔍 Reading Bill... Please wait."):
        # Perform OCR
        raw_text = pytesseract.image_to_string(image)
        
        # Extract Data using our smart function
        extracted_data = extract_info(raw_text)

    # --- Display Results ---
    st.success("Extraction Complete! ✅")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("👤 Name", extracted_data["Customer Name"])
    with col2:
        st.metric("💰 Amount", f"₹{extracted_data['Bill Amount']}")
    with col3:
        st.metric("⚡ Units", extracted_data["Units"])

    # --- Show Raw Text (Helpful for debugging) ---
    with st.expander("See Raw Scanned Text"):
        st.text(raw_text)

    # --- Export to Excel/CSV ---
    df = pd.DataFrame([extracted_data])
    csv = df.to_csv(index=False).encode('utf-8')
    
    st.download_button(
        label="📥 Download Results (CSV)",
        data=csv,
        file_name="extracted_bill_data.csv",
        mime="text/csv",
    )
