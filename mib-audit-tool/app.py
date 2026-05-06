import streamlit as st
import fitz  # PyMuPDF
import io
import pandas as pd
from docx import Document
from fpdf import FPDF

st.set_page_config(page_title="Secure Image-PDF Shield", layout="centered")

# UI Protection
st.markdown("""
    <style> body { -webkit-user-select: none; user-select: none; } </style>
    <script> document.addEventListener('contextmenu', event => event.preventDefault()); </script>
""", unsafe_allow_html=True)

st.title("🔐 Secure Image-PDF Shield")

with st.sidebar:
    st.header("လုံခြုံရေး")
    user_pw = st.text_input("ဖိုင်ဖွင့်ရန် Password သတ်မှတ်ပါ", type="password")

def excel_to_pdf_stream(file_bytes):
    df = pd.read_excel(io.BytesIO(file_bytes))
    pdf = FPDF(orientation='L', unit='mm', format='A4') # အလျားလိုက် (Landscape) ပြောင်းလိုက်တယ်
    pdf.add_page()
    pdf.set_font("Arial", size=9)
    
    # Error မတက်အောင် cell width ကို စာမျက်နှာအကျယ်အတိုင်း ပေးလိုက်ခြင်း
    page_width = pdf.w - 2 * pdf.l_margin
    
    for i in range(min(len(df), 200)): # အတန်း ၂၀၀ ထိ တိုးပေးထားတယ်
        row_text = " | ".join([str(v) for v in df.iloc[i].values])
        # w=0 ဆိုတာ စာမျက်နှာအဆုံးထိ အလိုအလျောက် ယူခိုင်းတာပါ
        pdf.multi_cell(w=0, h=8, txt=row_text, border=1)
    return pdf.output()

def word_to_pdf_stream(file_bytes):
    doc = Document(io.BytesIO(file_bytes))
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    for para in doc.paragraphs:
        if para.text.strip():
            # w=0 သုံးထားလို့ Horizontal space error မတက်တော့ပါ
            pdf.multi_cell(w=0, h=10, txt=para.text)
    return pdf.output()

def convert_to_secure_image_pdf(pdf_stream, password):
    doc = fitz.open(stream=pdf_stream, filetype="pdf")
    out_pdf = fitz.open()
    for page in doc:
        pix = page.get_pixmap(dpi=150)
        img_data = pix.tobytes("jpg", jpg_quality=75)
        new_page = out_pdf.new_page(width=page.rect.width, height=page.rect.height)
        new_page.insert_image(page.rect, stream=img_data)

    output_buffer = io.BytesIO()
    out_pdf.save(
        output_buffer,
        encryption=fitz.PDF_ENCRYPT_AES_256,
        user_pw=password if password else None,
        owner_pw="master_999",
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
            st.warning("Password အရင်ရိုက်ပေးပါ။")
        else:
            try:
                with st.spinner('Processing...'):
                    if file_ext == "pdf":
                        temp_pdf = file_bytes
                    elif file_ext == "xlsx":
                        temp_pdf = excel_to_pdf_stream(file_bytes)
                    elif file_ext == "docx":
                        temp_pdf = word_to_pdf_stream(file_bytes)
                    
                    final_pdf = convert_to_secure_image_pdf(temp_pdf, user_pw)
                    
                    st.success("✅ အောင်မြင်စွာ ပြောင်းလဲပြီးပါပြီ။")
                    st.download_button(
                        label="📥 Download Now",
                        data=final_pdf,
                        file_name=f"Secure_{uploaded_file.name.split('.')[0]}.pdf",
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"Error: {e}")
