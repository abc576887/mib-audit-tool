import streamlit as st
import fitz  # PyMuPDF
import io
import pandas as pd
from docx import Document
from fpdf import FPDF

# Page setup
st.set_page_config(page_title="Secure Image-PDF Shield", layout="centered")

# --- UI Protection ---
st.markdown("""
    <style> body { -webkit-user-select: none; user-select: none; } </style>
    <script> document.addEventListener('contextmenu', event => event.preventDefault()); </script>
""", unsafe_allow_html=True)

st.title("🔐 Secure Image-PDF Shield")

# Sidebar Settings
with st.sidebar:
    st.header("လုံခြုံရေး")
    user_pw = st.text_input("ဖိုင်ဖွင့်ရန် Password သတ်မှတ်ပါ", type="password")

def excel_to_pdf_stream(file_bytes):
    df = pd.read_excel(io.BytesIO(file_bytes))
    pdf = FPDF()
    pdf.add_page()
    # Font Error မတက်အောင် core font 'helvetica' (သို့) 'courier' ကို တိုက်ရိုက်သုံးပါသည်
    pdf.set_font("helvetica", size=10)
    
    for i in range(min(len(df), 100)):
        row_text = " | ".join([str(v) for v in df.iloc[i].values])
        pdf.multi_cell(0, 10, row_text, border=1)
    return pdf.output()

def word_to_pdf_stream(file_bytes):
    doc = Document(io.BytesIO(file_bytes))
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=11)
    
    for para in doc.paragraphs:
        if para.text.strip():
            pdf.multi_cell(0, 10, para.text)
    return pdf.output()

def convert_to_secure_image_pdf(pdf_stream, password):
    """စာသားကို ပုံပြောင်းပြီး Password ခံခြင်း"""
    doc = fitz.open(stream=pdf_stream, filetype="pdf")
    out_pdf = fitz.open()
    
    for page in doc:
        # DPI 140 နဲ့ JPG Quality 70 (ဖိုင်ဆိုဒ်သေးရန်)
        pix = page.get_pixmap(dpi=140)
        img_data = pix.tobytes("jpg", jpg_quality=70)
        
        new_page = out_pdf.new_page(width=page.rect.width, height=page.rect.height)
        new_page.insert_image(page.rect, stream=img_data)

    output_buffer = io.BytesIO()
    
    # Password ခံ၍ သိမ်းခြင်း
    out_pdf.save(
        output_buffer,
        encryption=fitz.PDF_ENCRYPT_AES_256,
        user_pw=password if password else None,
        owner_pw="master_key_123",
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
            st.warning("ဘယ်ဘက် Sidebar မှာ Password အရင်သတ်မှတ်ပါ။")
        else:
            try:
                with st.spinner('လုံခြုံရေးအတွက် လုပ်ဆောင်နေသည်...'):
                    if file_ext == "pdf":
                        temp_pdf = file_bytes
                    elif file_ext == "xlsx":
                        temp_pdf = excel_to_pdf_stream(file_bytes)
                    elif file_ext == "docx":
                        temp_pdf = word_to_pdf_stream(file_bytes)
                    
                    final_pdf = convert_to_secure_image_pdf(temp_pdf, user_pw)
                    
                    st.success("✅ အောင်မြင်စွာ လုပ်ဆောင်ပြီးပါပြီ။")
                    st.download_button(
                        label="📥 Download Protected PDF",
                        data=final_pdf,
                        file_name=f"Secure_{uploaded_file.name.split('.')[0]}.pdf",
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"Error: {e}")
