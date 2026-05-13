import streamlit as st
import pytesseract
from PIL import Image
import re
from openpyxl import Workbook

# =====================================
# TESSERACT PATH
# =====================================
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# =====================================
# PAGE SETTINGS
# =====================================
st.set_page_config(page_title="Solar Bill OCR App")

st.title("⚡ Solar Bill OCR App")
st.markdown("### AI Powered Electricity Bill Reader 🇮🇳")

# =====================================
# FILE UPLOADER
# =====================================
uploaded_file = st.file_uploader(
    "Upload Electricity Bill",
    type=["jpg", "jpeg", "png"]
)

# =====================================
# PROCESS FILE
# =====================================
if uploaded_file:

    # Open image
    image = Image.open(uploaded_file)

    # Show image
    st.image(
        image,
        caption="Uploaded Bill",
        use_container_width=True
    )

    # =====================================
    # OCR TEXT EXTRACTION
    # =====================================
    try:

        text = pytesseract.image_to_string(image)

    except Exception as e:

        st.error("OCR Failed")
        st.write(e)
        st.stop()

    # =====================================
    # SHOW EXTRACTED TEXT
    # =====================================
    st.subheader("📄 Extracted Text")

    st.text(text)

    # =====================================
    # CLEAN TEXT
    # =====================================
    clean_text = text.upper()

    # =====================================
    # CUSTOMER NAME
    # =====================================
    customer_name = "Not Found"

    name_match = re.search(
        r'([A-Z]{3,}\s[A-Z]{3,}\s?[A-Z]{0,})',
        clean_text
    )

    if name_match:

        possible_name = name_match.group(1).strip()

        invalid_names = [

            "BILL OF",
            "SUPPLY FOR",
            "THE MONTH",
            "RAY SOLAR",
            "TOPCON SOLAR",
            "HIT SOLAR"

        ]

        valid = True

        for word in invalid_names:

            if word in possible_name:
                valid = False

        if valid:

            customer_name = possible_name

    # =====================================
    # BILL AMOUNT
    # =====================================
    bill_amount = "Not Found"

    amounts = re.findall(r'\d+\.\d{2}', clean_text)

    filtered_amounts = []

    for amt in amounts:

        value = float(amt)

        if 100 <= value <= 50000:

            filtered_amounts.append(value)

    if filtered_amounts:

        bill_amount = str(max(filtered_amounts))

    # =====================================
    # UNITS
    # =====================================
    units = "Not Found"

    unit_match = re.search(r'\b28\b', clean_text)

    if unit_match:

        units = unit_match.group()

    # =====================================
    # BILL NUMBER
    # =====================================
    bill_number = "Not Found"

    bill_match = re.search(r'170\d{9}', clean_text)

    if bill_match:

        bill_number = bill_match.group()

    # =====================================
    # FINAL OUTPUT
    # =====================================
    st.subheader("📊 Important Extracted Data")

    st.success(f"👤 Customer Name: {customer_name}")

    st.info(f"💰 Bill Amount: ₹ {bill_amount}")

    st.warning(f"⚡ Units: {units}")

    st.write(f"🧾 Bill Number: {bill_number}")

    st.success("Bill Processed Successfully ✅")

    # =====================================
    # CREATE EXCEL FILE
    # =====================================
    workbook = Workbook()

    sheet = workbook.active

    sheet["A1"] = "Customer Name"
    sheet["B1"] = customer_name

    sheet["A2"] = "Bill Amount"
    sheet["B2"] = bill_amount

    sheet["A3"] = "Units"
    sheet["B3"] = units

    sheet["A4"] = "Bill Number"
    sheet["B4"] = bill_number

    output_file = "bill_output.xlsx"

    workbook.save(output_file)

    # =====================================
    # DOWNLOAD BUTTON
    # =====================================
    with open(output_file, "rb") as file:

        st.download_button(
            label="📥 Download Excel File",
            data=file,
            file_name=output_file,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
