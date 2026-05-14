import streamlit as st
import pytesseract
from PIL import Image
import re
from io import BytesIO
from openpyxl import Workbook

st.set_page_config(page_title="Universal Bill Reader", layout="centered")

st.title("⚡ Universal Bill OCR")
st.write("Upload any electricity or solar bill to extract data automatically.")

uploaded_file = st.file_uploader("Choose a bill image...", type=["jpg", "png", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)
    
    with st.spinner("🔍 AI is reading your bill..."):
        # 1. OCR Extraction
        text = pytesseract.image_to_string(image)
        
        # 2. Logic to find data
        # (Using the regex logic from the previous message)
        # ... [Insert regex extraction logic here] ...

        # 3. Display Results
        st.success("Data Extracted Successfully!")
        # ... [Display metrics and Download Button] ...
