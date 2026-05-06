import streamlit as st
import fitz  # PyMuPDF
import io
import pandas as pd
from docx import Document
from fpdf import FPDF

# Page setup
st.set_page_config(page_title="Secure Image-PDF Converter", layout="centered")

# --- UI Protection ---
st.markdown("""
    <style> body { -webkit-user-select: none; user-select: none; } </style>
    <script> document.addEventListener('contextmenu', event => event.preventDefault()); </script>
""", unsafe_allow_html=True)

st.title("🔐 Secure Image-PDF Converter")

# Sidebar မှာ Password သတ်မှတ်ရန်
with st.sidebar:
    st.header("လုံခြုံရေး")
    user_pw = st.text_input("ဖိုင်ဖွင့်ရန် Password သတ်မှတ်ပါ", type="password", help="ဒီ Password ရှိမှ ဖိုင်ကို ဖွင့်ကြည့်လို့ရပါမယ်")

def excel_to_pdf_stream(file_bytes):
    df = pd.read_excel(io.BytesIO(file_bytes))
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    for i in range(min(len(df), 100)):
        row_text = " | ".join([str(v) for v in df.iloc[i].values])
        pdf.multi_cell(0, 10, row_text, border=1)
    return pdf.output()

def word_to_pdf_stream(file_bytes):
    doc = Document(io.BytesIO(file_bytes))
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    for para in doc.paragraphs:
        if para.text.strip():
            pdf.multi_cell(0, 10, para.text)
    return pdf.output()

def convert_to_secure_image_pdf(pdf_stream, password):
    """စာသားကို ပုံပြောင်းပြီး Password ခံခြင်း"""
    doc = fitz.open(stream=pdf_stream, filetype="pdf")
    out_pdf = fitz.open()
    
    for page in doc:
        # DPI 150 နဲ့ JPG Quality 75
        pix = page.get_pixmap(dpi=150)
        img_data = pix.tobytes("jpg", jpg_quality=75)
        
        new_page = out_pdf.new_page(width=page.rect.width, height=page.rect.height)
        new_page.insert_image(page.rect, stream=img_data)

    output_buffer = io.BytesIO()
    
    # Password ခံပြီး သိမ်းဆည်းခြင်း
    # owner_pw ကို master key အဖြစ် အသေထားထားပါတယ်
    out_pdf.save(
        output_buffer,
        encryption=fitz.PDF_ENCRYPT_AES_256,
        user_pw=password if password else None,
        owner_pw="master_admin_123",
        deflate=True
    )
    doc.close()
    out_pdf.close()
    return output_buffer.getvalue()

uploaded_file = st.file_uploader("ဖိုင်ရွေးပါ (Word, Excel, PDF)", type=["pdf", "docx", "xlsx"])

if uploaded_file:
    file_ext = uploaded_file.name.split('.')[-1].lower()
    file_bytes = uploaded_file.read()
    
    if st.button("🚀 Password ဖြင့် PDF ပြောင်းမည်"):
        if not user_pw:
            st.warning("ဘယ်ဘက် Sidebar မှာ Password အရင်သတ်မှတ်ပေးပါဦး။")
        else:
            try:
                with st.spinner('လုံခြုံရေးအတွက် လုပ်ဆောင်နေသည်...'):
                    # ၁။ PDF အရင်ပြောင်း
                    if file_ext == "pdf":
                        temp_pdf = file_bytes
                    elif file_ext == "xlsx":
                        temp_pdf = excel_to_pdf_stream(file_bytes)
                    elif file_ext == "docx":
                        temp_pdf = word_to_pdf_stream(file_bytes)
                    
                    # ၂။ Image-based ဖြစ်အောင်လုပ်ပြီး Password ခံ
                    final_pdf = convert_to_secure_image_pdf(temp_pdf, user_pw)
                    
                    st.success(f"✅ Password ဖြင့် ကာကွယ်ပြီးပါပြီ။")
                    st.download_button(
                        label="📥 Download Protected PDF",
                        data=final_pdf,
                        file_name=f"Protected_{uploaded_file.name.split('.')[0]}.pdf",
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("""
---
### 🛡️ ဒီ Version ရဲ့ ထူးခြားချက်:
1.  **Open Password:** Sidebar မှာ ရိုက်ထားတဲ့ Password ရှိမှ ဖိုင်ကို ဖွင့်ကြည့်လို့ ရပါမယ်။
2.  **No Copying:** စာသားတွေက ပုံရိပ်တွေ ဖြစ်သွားတဲ့အတွက် ဖိုင်ပွင့်လာရင်တောင် Copy ကူးလို့ မရပါဘူး။
3.  **Auto Conversion:** Word နဲ့ Excel ကို အလိုအလျောက် PDF ပြောင်းပေးပါတယ်။
""")
