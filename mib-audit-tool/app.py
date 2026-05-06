import streamlit as st
import fitz  # PyMuPDF
import io
import pandas as pd
from docx import Document
from fpdf import FPDF

# Page setup
st.set_page_config(page_title="Universal Auto-PDF Shield", layout="centered")

# --- UI Protection (Copy/Selection ပိတ်ခြင်း) ---
st.markdown("""
    <style> body { -webkit-user-select: none; user-select: none; } </style>
    <script> document.addEventListener('contextmenu', event => event.preventDefault()); </script>
""", unsafe_allow_html=True)

st.title("🛡️ Universal Auto-PDF Converter")
st.info("Excel, Word, PDF ဘာတင်တင် Copy ကူးမရတဲ့ PDF အဖြစ် အလိုအလျောက် ပြောင်းပေးပါမယ်။")

# Sidebar Security
with st.sidebar:
    st.header("လုံခြုံရေး ဆက်တင်")
    user_pw = st.text_input("ဖိုင်ဖွင့်ရန် Password (မခံချင်ရင် အလွတ်ထားပါ)", type="password")
    owner_pw = "master_key_123"

def excel_to_pdf_stream(file_bytes):
    """Excel ကို PDF သို့ အလိုအလျောက်ပြောင်းခြင်း"""
    df = pd.read_excel(io.BytesIO(file_bytes))
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    # ဇယားခေါင်းစဉ်များ
    cols = df.columns.tolist()
    line_text = " | ".join([str(c) for c in cols])
    pdf.multi_cell(0, 10, line_text, border=1)
    # Data အတန်းများ (နမူနာ ၅၀ ထိ)
    for i in range(min(len(df), 50)):
        row_text = " | ".join([str(v) for v in df.iloc[i].values])
        pdf.multi_cell(0, 10, row_text, border=1)
    return pdf.output()

def word_to_pdf_stream(file_bytes):
    """Word ကို PDF သို့ အလိုအလျောက်ပြောင်းခြင်း"""
    doc = Document(io.BytesIO(file_bytes))
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    for para in doc.paragraphs:
        if para.text.strip():
            pdf.multi_cell(0, 10, para.text)
    return pdf.output()

def finalize_to_image_pdf(pdf_stream, u_pw, o_pw):
    """PDF ကို Copy ကူးမရအောင် Image-based လုပ်ပြီး ဆိုဒ်ချုံ့ခြင်း"""
    doc = fitz.open(stream=pdf_stream, filetype="pdf")
    out_pdf = fitz.open()
    
    for page in doc:
        # DPI 140 နဲ့ JPG Quality 70 သုံးပြီး ဆိုဒ်ချုံ့ပါတယ်
        pix = page.get_pixmap(dpi=140)
        img_data = pix.tobytes("jpg", jpg_quality=70)
        
        new_page = out_pdf.new_page(width=page.rect.width, height=page.rect.height)
        new_page.insert_image(page.rect, stream=img_data)

    perm = int(fitz.PDF_PERM_ACCESSIBILITY | 0)
    output_buffer = io.BytesIO()
    out_pdf.save(
        output_buffer,
        encryption=fitz.PDF_ENCRYPT_AES_256,
        user_pw=u_pw if u_pw else None,
        owner_pw=o_pw,
        permissions=perm,
        deflate=True
    )
    doc.close()
    out_pdf.close()
    return output_buffer.getvalue()

uploaded_file = st.file_uploader("ဖိုင်ရွေးချယ်ပါ", type=["pdf", "docx", "xlsx"])

if uploaded_file:
    file_ext = uploaded_file.name.split('.')[-1].lower()
    file_bytes = uploaded_file.read()
    
    if st.button("🚀 PDF အဖြစ်ပြောင်းပြီး Download ဆွဲမည်"):
        try:
            with st.spinner('အနောက်ကွယ်တွင် PDF ပြောင်းလဲပြီး Image-based PDF အဖြစ် ကာကွယ်နေသည်...'):
                # ၁။ ဖိုင်အမျိုးအစားအလိုက် PDF အရင်ပြောင်း
                if file_ext == "pdf":
                    temp_pdf = file_bytes
                elif file_ext == "xlsx":
                    temp_pdf = excel_to_pdf_stream(file_bytes)
                elif file_ext == "docx":
                    temp_pdf = word_to_pdf_stream(file_bytes)
                
                # ၂။ Copy ကူးမရအောင် Image PDF အဖြစ် အပြီးသတ်ပြောင်း
                final_pdf = finalize_to_image_pdf(temp_pdf, user_pw, owner_pw)
                
                st.success(f"✅ လုပ်ဆောင်ပြီးပါပြီ။ ဖိုင်ဆိုဒ်: {len(final_pdf)/1024:.1f} KB")
                st.download_button(
                    label="📥 Download Protected PDF",
                    data=final_pdf,
                    file_name=f"Secure_{uploaded_file.name.split('.')[0]}.pdf",
                    mime="application/pdf"
                )
        except Exception as e:
            st.error(f"Error: {e}. (ဖိုင်အရမ်းရှုပ်ထွေးလျှင် PDF အဖြစ် Save ပြီးမှ တင်ပေးပါ)")

st.markdown("""
---
### 💡 အလုပ်လုပ်ပုံ အဆင့်ဆင့်-
1. သင်က **Excel** သို့မဟုတ် **Word** ကို တိုက်ရိုက်တင်လိုက်ပါ။
2. App က အနောက်ကွယ်မှာ PDF အဖြစ် အလိုအလျောက် ပြောင်းပေးပါမယ်။
3. ရလာတဲ့ PDF ကို **Image (ပုံရိပ်)** အဖြစ် ထပ်ပြောင်းလိုက်လို့ ဘယ်သူမှ Copy ကူးလို့ မရတော့ပါဘူး။
4. ဖိုင်ဆိုဒ်သေးအောင်လည်း JPG နည်းပညာနဲ့ ချုံ့ပေးထားပါတယ်။
""")
