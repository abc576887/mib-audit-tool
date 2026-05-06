import streamlit as st
import fitz  # PyMuPDF
import io
import pandas as pd
from docx import Document
from fpdf import FPDF

st.set_page_config(page_title="Pro Secure Doc Shield", layout="centered")

# --- UI Protection ---
st.markdown("""
    <style> body { -webkit-user-select: none; user-select: none; } </style>
    <script> document.addEventListener('contextmenu', event => event.preventDefault()); </script>
    """, unsafe_allow_html=True)

def excel_to_pdf(excel_file):
    """Excel data ကို ယာယီ PDF တစ်ခုအဖြစ် ပြောင်းလဲခြင်း"""
    df = pd.read_excel(excel_file)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    
    # ဇယားခေါင်းစဉ်များ
    cols = df.columns.tolist()
    for col in cols:
        pdf.cell(40, 10, str(col), border=1)
    pdf.ln()
    
    # Data များ (နမူနာ အတန်း ၅၀ ထိသာ ထည့်သွင်းပေးထားပါသည် - ဆိုဒ်မကြီးစေရန်)
    for i in range(min(len(df), 50)):
        for col in cols:
            pdf.cell(40, 10, str(df.iloc[i][col]), border=1)
        pdf.ln()
    
    return pdf.output()

def protect_document(pdf_bytes, u_pw, o_pw):
    """PDF ကို Rasterize လုပ်ပြီး Permission များ ပိတ်ခြင်း"""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    out_pdf = fitz.open()
    
    for page in doc:
        pix = page.get_pixmap(dpi=150)
        img_data = pix.tobytes("jpg", jpg_quality=70)
        new_page = out_pdf.new_page(width=page.rect.width, height=page.rect.height)
        new_page.insert_image(page.rect, stream=img_data)

    perm = int(fitz.PDF_PERM_ACCESSIBILITY | 0)
    output_buffer = io.BytesIO()
    out_pdf.save(output_buffer, encryption=fitz.PDF_ENCRYPT_AES_256,
                 user_pw=u_pw if u_pw else None, owner_pw=o_pw,
                 permissions=perm, deflate=True)
    out_pdf.close()
    return output_buffer.getvalue()

st.title("🛡️ Multi-Doc Security Shield")
uploaded_file = st.file_uploader("ဖိုင်ရွေးချယ်ပါ", type=["pdf", "docx", "xlsx"])

if uploaded_file:
    file_ext = uploaded_file.name.split('.')[-1].lower()
    owner_pw = "master_key_123"
    
    try:
        with st.spinner('Processing...'):
            if file_ext == "pdf":
                pdf_input = uploaded_file.read()
            elif file_ext == "xlsx":
                # Excel ကို အရင် PDF ပြောင်းမယ်
                pdf_input = excel_to_pdf(uploaded_file)
            elif file_ext == "docx":
                # Word viewer logic (Simplified for this example)
                st.error("Word processing requires additional layout settings.")
                st.stop()
            
            final_data = protect_document(pdf_input, "", owner_pw)

            if final_data:
                st.success(f"✅ လုပ်ဆောင်ပြီးပါပြီ။")
                st.download_button(
                    label="Download Protected PDF",
                    data=final_data,
                    file_name=f"Protected_{uploaded_file.name.split('.')[0]}.pdf",
                    mime="application/pdf"
                )
    except Exception as e:
        st.error(f"Error: {e}")
