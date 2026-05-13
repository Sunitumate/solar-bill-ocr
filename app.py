import streamlit as st
import pytesseract
from PIL import Image
import re
from openpyxl import Workbook

# =====================================
# PAGE SETTINGS
# =====================================

st.set_page_config(
    page_title="Solar Bill OCR App",
    layout="centered"
)

st.title("⚡ Solar Bill OCR App")
st.markdown("### AI Powered Electricity Bill Reader 🇮🇳")

# =====================================
# TESSERACT PATH
# =====================================

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# =====================================
# FILE UPLOADER
# =====================================

uploaded_file = st.file_uploader(
    "Upload Electricity Bill",
    type=["jpg", "jpeg", "png"]
)

# =====================================
# PROCESS BILL
# =====================================

if uploaded_file:

    # Open image
    image = Image.open(uploaded_file)

    # Show uploaded image
    st.image(
        image,
        caption="Uploaded Bill",
        use_container_width=True
    )

    # =====================================
    # OCR EXTRACTION
    # =====================================

    try:

        text = pytesseract.image_to_string(image)

    except Exception as e:

        st.error("OCR Failed")
        st.write(e)
        st.stop()

    # =====================================
    # SHOW OCR TEXT
    # =====================================

    st.subheader("📄 Extracted Text")
    st.text(text)

    # =====================================
    # CLEAN TEXT
    # =====================================

    clean_text = text.upper()

    # =====================================
    # EXTRACT CUSTOMER NAME
    # =====================================

    name = "Not Found"

    single_line_text = clean_text.replace("\n", " ")

    name_patterns = [

        r'([A-Z]{3,}\s+[A-Z]{3,}\s+[A-Z]{3,})',

        r'([A-Z]{3,}\s+[A-Z]{3,})'
    ]

    for pattern in name_patterns:

        matches = re.findall(pattern, single_line_text)

        for match in matches:

            skip_names = [

                "BILL OF SUPPLY",
                "FOR THE MONTH",
                "GSTIN",
                "RAY SOLAR",
                "CGRF",
                "PAYMENT",
                "APPROVED",
                "SCAN QR",
                "INDIA LEADING",
                "TOPCON SOLAR",
                "SOLAR PANELS"

            ]

            if any(skip in match for skip in skip_names):
                continue

            name = match.strip()
            break

        if name != "Not Found":
            break

    # =====================================
    # EXTRACT BILL AMOUNT
    # =====================================

    bill_amount = "Not Found"

    amount_patterns = [

        r'RS\.?\s?(\d+\.\d+)',

        r'RS\.?\s?(\d+)',

        r'(\d+\.\d+)\s?RS'
    ]

    for pattern in amount_patterns:

        matches = re.findall(pattern, clean_text)

        if matches:

            values = []

            for m in matches:

                try:
                    values.append(float(m))
                except:
                    pass

            if values:

                bill_amount = max(values)
                break

    # =====================================
    # EXTRACT UNITS
    # =====================================

    units = "Not Found"

    unit_patterns = [

        r'UNITS?\s*[:\-]?\s*(\d+)',

        r'CONSUMPTION\s*[:\-]?\s*(\d+)',

        r'\b(\d{1,4})\b'
    ]

    for pattern in unit_patterns:

        matches = re.findall(pattern, clean_text)

        for match in matches:

            value = int(match)

            if 1 <= value <= 5000:

                units = value
                break

        if units != "Not Found":
            break

    # =====================================
    # EXTRACT BILL NUMBER
    # =====================================

    bill_number = "Not Found"

    bill_patterns = [

        r'CONSUMER\s*NO\.?\s*[:\-]?\s*(\d+)',

        r'BILL\s*NO\.?\s*[:\-]?\s*(\d+)',

        r'(\d{12})'
    ]

    for pattern in bill_patterns:

        matches = re.findall(pattern, clean_text)

        if matches:

            bill_number = matches[0]
            break

    # =====================================
    # FINAL OUTPUT
    # =====================================

    st.subheader("📊 Important Extracted Data")

    st.success(f"👤 Customer Name: {name}")

    st.info(f"💰 Bill Amount: ₹ {bill_amount}")

    st.warning(f"⚡ Units: {units}")

    st.success(f"🧾 Bill Number: {bill_number}")

    st.success("Bill Processed Successfully ✅")

    # =====================================
    # CREATE EXCEL FILE
    # =====================================

    workbook = Workbook()

    sheet = workbook.active

    sheet.title = "Bill Data"

    sheet["A1"] = "Customer Name"
    sheet["B1"] = name

    sheet["A2"] = "Bill Amount"
    sheet["B2"] = bill_amount

    sheet["A3"] = "Units"
    sheet["B3"] = units

    sheet["A4"] = "Bill Number"
    sheet["B4"] = bill_number

    output_file = "solar_bill_output.xlsx"

    workbook.save(output_file)

    # =====================================
    # DOWNLOAD BUTTON
    # =====================================

    with open(output_file, "rb") as file:

        st.download_button(
            label="📥 Download Excel File",
            data=file,
            file_name="solar_bill_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
