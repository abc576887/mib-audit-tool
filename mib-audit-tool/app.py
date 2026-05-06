import streamlit as st
import fitz  # PyMuPDF
import io
import pandas as pd
from docx import Document

# Page setup
st.set_page_config(page_title="Universal Secure Shield", layout="centered")

# --- UI Protection ---
st.markdown("""
    <style> body { -webkit-user-select: none; user-select: none; } </style>
    <script> document.addEventListener('contextmenu', event => event.preventDefault()); </script>
""", unsafe_allow_html=True)

st.title("🛡️ Universal Secure PDF Shield")
st.info("Excel, Word, PDF အားလုံးကို Image-PDF သို့ ပြောင်းပေးမည်။ (Layout မပျက်စေရန် PDF အဖြစ် အရင်ပြောင်းပြီး တင်ခြင်းကို ပိုမိုအကြံပြုပါသည်။)")

# Sidebar Settings
with st.sidebar:
    st.header("Security Settings")
    user_pw = st.text_input("Open Password (Optional)", type="password")
    owner_pw = "admin_master_123"

def finalize_to_image_pdf(pdf_stream, u_pw, o_pw):
    """Layout ထိန်းသိမ်းပြီး Image PDF ပြောင်းခြင်း"""
    doc = fitz.open(stream=pdf_stream, filetype="pdf")
    out_pdf = fitz.open()
    
    for page in doc:
        # DPI 140 သည် စာဖတ်ရတာကြည်လင်ပြီး ဆိုဒ်လည်း သေးစေပါသည်
        pix = page.get_pixmap(dpi=140)
        img_data = pix.tobytes("jpg", jpg_quality=70) # JPG quality 70% သုံး၍ ဆိုဒ်ချုံ့ခြင်း
        
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

uploaded_file = st.file_uploader("ဖိုင်တင်ပါ (PDF, DOCX, XLSX)", type=["pdf", "docx", "xlsx"])

if uploaded_file:
    file_ext = uploaded_file.name.split('.')[-1].lower()
    file_data = uploaded_file.read()
    
    if st.button("Generate Secure Image-PDF"):
        try:
            with st.spinner('လုံခြုံရေးအတွက် လုပ်ဆောင်နေသည်...'):
                
                # ၁။ PDF သို့ အရင်ပြောင်းလဲခြင်း logic
                if file_ext == "pdf":
                    temp_pdf = file_data
                elif file_ext == "xlsx":
                    # Excel ကို HTML/PDF ပြောင်းလဲရန် (ရိုးရှင်းသော ဇယားများအတွက်သာ)
                    df = pd.read_excel(io.BytesIO(file_data))
                    st.warning("Excel Layout တိကျစေရန် PDF အဖြစ် Save ပြီးမှ တင်ပေးပါ။")
                    st.stop()
                elif file_ext == "docx":
                    # Word Layout တိကျစေရန်
                    st.warning("Word Layout တိကျစေရန် PDF အဖြစ် Save ပြီးမှ တင်ပေးပါ။")
                    st.stop()
                
                # ၂။ Image-based PDF အဖြစ် အပြီးသတ်ပြောင်းလဲခြင်း
                final_pdf = finalize_to_image_pdf(temp_pdf, user_pw, owner_pw)
                
                st.success(f"✅ လုပ်ဆောင်ပြီးပါပြီ။ ဖိုင်ဆိုဒ်: {len(final_pdf)/1024:.1f} KB")
                st.download_button(
                    label="📥 Download Protected PDF",
                    data=final_pdf,
                    file_name=f"Secure_{uploaded_file.name.split('.')[0]}.pdf",
                    mime="application/pdf"
                )
        except Exception as e:
            st.error(f"Error: {e}")

st.markdown("""
---
### 💡 Layout မပျက်အောင် ဘယ်လိုလုပ်မလဲ?
1. **Excel/Word** ကို ဖွင့်ပါ။
2. **File > Save As** ကို နှိပ်ပြီး **PDF** format ကို ရွေး၍ သိမ်းပါ။
3. ထိုရလာသော PDF ကို ဤ App ထဲသို့ တင်ပေးပါ။
4. App က Layout ၁၀၀% မပျက်စေဘဲ Copy ကူးမရသော Image-PDF အဖြစ် ပြောင်းပေးပါလိမ့်မည်။
""")
