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
    # 1. Improved Amount Logic: 
    # Looks for numbers after 'Total', 'Net', or 'Payable' even without 'Rs'
    amt_match = re.search(r'(?:Total|Net|Payable|Amount|Rs|₹)[\s\.:]*([\d,]+\.\d{2})', text, re.IGNORECASE)
    bill_amt = amt_match.group(1).replace(',', '') if amt_match else "Not Found"

    # 2. Improved Units Logic:
    # Specifically looks for the word 'Units' or 'KWh' followed by a number
    unit_match = re.search(r'(?:Units|Consumed|KWh|Usage)[\s\.:]*(\d+)', text, re.IGNORECASE)
    units = unit_match.group(1) if unit_match else "Not Found"

    # 3. Improved Name Logic:
    # Skips lines that look like phone numbers (digits only) or contain common bill keywords
    lines = text.split('\n')
    name = "Not Found"
    for line in lines:
        clean = line.strip()
        # Ensure line has letters, is long enough, and isn't just a phone number
        if len(clean) > 8 and any(c.isalpha() for c in clean):
            bad_words = ['bill', 'date', 'tax', 'no', 'tel', 'phone', 'account', 'consumer']
            if not any(word in clean.lower() for word in bad_words):
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
