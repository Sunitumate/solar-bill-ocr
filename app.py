import streamlit as st
import pytesseract
from PIL import Image
import re
from openpyxl import Workbook
from io import BytesIO

# --- FOR WINDOWS USERS ---
# If you get a TesseractNotFoundError, uncomment the line below and point it to your install:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

st.set_page_config(page_title="Solar Bill OCR App", layout="centered")

st.title("⚡ Solar Bill OCR App")
st.markdown("### AI Powered Electricity Bill Reader")

uploaded_file = st.file_uploader("Upload Bill Image", type=["jpg", "png", "jpeg"])
def extract_data(text):
    # 1. UNIVERSAL AMOUNT LOGIC
    # Searches for common currency symbols and decimal formats
    amt_match = re.search(r'(?:Total|Net|Payable|Amount|Rs|₹|Bill)[\s\.:]*([\d,]+\.\d{2})', text, re.IGNORECASE)
    bill_amt = amt_match.group(1).replace(',', '') if amt_match else "Not Found"

    # 2. UNIVERSAL UNITS LOGIC
    # Covers KWH, Units, and Consumed energy
    unit_match = re.search(r'(?:Units|Consumed|KWh|Usage|Total|Reading)[\s\.:]*(\d+)', text, re.IGNORECASE)
    units = unit_match.group(1) if unit_match else "Not Found"

    # 3. UNIVERSAL NAME LOGIC (The hardest part for public apps)
    lines = text.split('\n')
    name = "Not Found"
    
    # We filter out lines that are likely dates, phone numbers, or addresses
    for line in lines:
        clean = line.strip()
        # A name must have letters, no numbers like '2026', and be long enough
        if len(clean) > 10 and any(c.isalpha() for c in clean):
            # Exclude lines that are clearly NOT names
            exclusions = ['bill', 'date', 'tax', 'no', 'tel', 'account', 'consumer', 'limited', 'highway', 'road', 'street']
            if not any(word in clean.lower() for word in exclusions):
                # Check if the line is NOT just a long number (like a Consumer ID)
                if not re.search(r'\d{8,}', clean): 
                    name = clean
                    break
            
    return name, bill_amt, units
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Bill")

    with st.spinner("🤖 AI is reading your bill..."):
        # ❗ ACTUAL OCR LOGIC
        raw_text = pytesseract.image_to_string(image)
        
        # Extract dynamic data
        name, bill_amount, units = extract_data(raw_text)

    # Display results
    st.subheader("Important Extracted Data")
    st.success(f"👤 Customer Name: {name}")
    st.info(f"💰 Bill Amount: {bill_amount}")
    st.warning(f"⚡ Units: {units}")

    # Create Excel file
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["Customer Name", name])
    sheet.append(["Bill Amount", bill_amount])
    sheet.append(["Units", units])

    # Save to memory
    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    st.download_button(
        label="📥 Download Excel File",
        data=output,
        file_name=f"{name}_bill.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    with st.expander("Show Raw Scanned Text"):
        st.text(raw_text)
