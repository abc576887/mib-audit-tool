import streamlit as st
import fitz  # PyMuPDF
import io
from docx import Document
import pandas as pd
from fpdf import FPDF

# Page setup
st.set_page_config(page_title="Pro Secure Doc Shield", layout="centered")

# --- UI Protection ---
st.markdown("""
    <style>
    body { -webkit-user-select: none; user-select: none; }
    </style>
    <script>
    document.addEventListener('contextmenu', event => event.preventDefault());
    </script>
    """, unsafe_allow_html=True)

st.title("🛡️ Pro Document Security Shield")

# --- Function: Word to Temporary PDF (Layout Focus) ---
def word_to_pdf_stream(docx_bytes):
    doc = Document(io.BytesIO(docx_bytes))
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # မြန်မာစာအတွက် Font Support ထည့်လိုပါက pdf.add_font(...) ဤနေရာတွင် သုံးနိုင်သည်
    pdf.set_font("Arial", size=11)
    
    for para in doc.paragraphs:
        # Paragraph align ကို အနီးစပ်ဆုံးယူခြင်း
        align = 'L'
        if para.alignment == 1: align = 'C'
        elif para.alignment == 2: align = 'R'
        
        # Multi-cell သုံးခြင်းဖြင့် စာကြောင်းရှည်လျှင် အလိုအလျောက် ဆင်းပေးသည် (Layout ထိန်းရန်)
        pdf.multi_cell(0, 10, txt=para.text, align=align)
    
    return pdf.output(dest='S').encode('latin-1', errors='replace')

# --- Function: Excel to Temporary PDF ---
def excel_to_pdf_stream(xlsx_bytes):
    df = pd.read_excel(io.BytesIO(xlsx_bytes))
    pdf = FPDF(orientation='L') # Excel အတွက် Landscape
    pdf.add_page()
    pdf.set_font("Arial", size=9)
    
    # Column အကျယ်ကို ချိန်ညှိခြင်း
    col_width = pdf.epw / len(df.columns)
    
    # Header
    for col in df.columns:
        pdf.cell(col_width, 10, str(col), border=1)
    pdf.ln()
    
    # Data
    for _, row in df.iterrows():
        for val in row:
            pdf.cell(col_width, 10, str(val), border=1)
        pdf.ln()
        
    return pdf.output(dest='S').encode('latin-1', errors='replace')

# --- Function: Protect & Rasterize ---
def protect_document(pdf_bytes, u_pw, o_pw):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    out_pdf = fitz.open()
    
    for page in doc:
        # DPI 150 + JPG Quality 70 (ဖိုင်ဆိုဒ်သေးပြီး ကြည်လင်ရန်)
        pix = page.get_pixmap(dpi=150)
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
    
    out_pdf.close()
    doc.close()
    return output_buffer.getvalue()

uploaded_file = st.file_uploader("ဖိုင်ရွေးချယ်ပါ (PDF, DOCX, XLSX)", type=["pdf", "docx", "xlsx"])

if uploaded_file is not None:
    file_ext = uploaded_file.name.split('.')[-1].lower()
    owner_pw = "master_admin_key_123"
    
    if st.button("🚀 Process & Protect"):
        try:
            with st.spinner('Converting & Securing...'):
                raw_bytes = uploaded_file.read()
                
                # ၁။ ဖိုင်အမျိုးအစားအလိုက် PDF သို့ အရင်ပြောင်းခြင်း
                if file_ext == "pdf":
                    temp_pdf_bytes = raw_bytes
                elif file_ext == "docx":
                    temp_pdf_bytes = word_to_pdf_stream(raw_bytes)
                elif file_ext == "xlsx":
                    temp_pdf_bytes = excel_to_pdf_stream(raw_bytes)
                
                # ၂။ ၎င်း PDF ကို Image-based ပြုလုပ်ပြီး Security ထည့်ခြင်း
                final_data = protect_document(temp_pdf_bytes, "", owner_pw)

                if final_data:
                    st.success(f"✅ အောင်မြင်စွာ လုပ်ဆောင်ပြီးပါပြီ။ (Size: {len(final_data)/1024:.2f} KB)")
                    st.download_button(
                        label="📥 Download Protected PDF",
                        data=final_data,
                        file_name=f"Protected_{uploaded_file.name.split('.')[0]}.pdf",
                        mime="application/pdf"
                    )
        except Exception as e:
            st.error(f"Error: {e}")
