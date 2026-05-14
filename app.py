import streamlit as st
import pytesseract
from PIL import Image
import pandas as pd
import re

# Title of the app
st.title("⚡ Simple Electricity Bill Reader")

# Uploading the file
uploaded_file = st.file_uploader("Choose a bill image...", type=["jpg", "png", "jpeg"])

def extract_info(text):
    data = {"Customer Name": "Not Found", "Bill Amount": "Not Found", "Units": "Not Found"}
    
    # 1. Simple search for Amount
    amt_match = re.search(r'(?:Rs|Amount|Total)[:\s]*(\d+\.?\d*)', text, re.IGNORECASE)
    if amt_match:
        data["Bill Amount"] = amt_match.group(1)
        
    # 2. Simple search for Units
    unit_match = re.search(r'(?:Units|Consumed)[:\s]*(\d+)', text, re.IGNORECASE)
    if unit_match:
        data["Units"] = unit_match.group(1)
        
    # 3. Simple search for Name (First long line with letters)
    lines = text.split('\n')
    for line in lines:
        clean = line.strip()
        if len(clean) > 8 and any(c.isalpha() for c in clean):
            if not any(word in clean.lower() for word in ['bill', 'date', 'account', 'consumer']):
                data["Customer Name"] = clean
                break
                
    return data

if uploaded_file:
    # Show the image
    img = Image.open(uploaded_file)
    st.image(img, caption="Uploaded Bill", use_container_width=True)
    
    with st.spinner("Reading data..."):
        # The OCR Part
        extracted_text = pytesseract.image_to_string(img)
        
        # Get the fields
        info = extract_info(extracted_text)
        
    # Display Results
    st.success("Done!")
    st.subheader("Extracted Results:")
    st.write(f"👤 **Name:** {info['Customer Name']}")
    st.write(f"💰 **Amount:** ₹{info['Bill Amount']}")
    st.write(f"⚡ **Units:** {info['Units']}")
    
    # Simple Download Button
    df = pd.DataFrame([info])
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Result as CSV", csv, "bill_result.csv", "text/csv")
