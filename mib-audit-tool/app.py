import streamlit as st
import fitz  # PyMuPDF
import io
from docx import Document
import pandas as pd
import aspose.words as aw

# Page setup
st.set_page_config(page_title="Pro Secure Doc Shield", layout="centered")

# --- UI Protection (Right-click & Selection ပိတ်ခြင်း) ---
# --- UI Protection ---
st.markdown("""
    <style>
    body { -webkit-user-select: none; user-select: none; }
@@ -24,7 +23,7 @@
    """, unsafe_allow_html=True)

st.title("🛡️ Pro Document Security Shield")
st.info("ဖိုင်ဆိုဒ်ကို ချုံ့ပေးထားပြီး Copy/Print ပိတ်ထားသော PDF အဖြစ် ပြောင်းလဲပေးမည်။")
st.info("Word သို့မဟုတ် PDF ကို Layout မပျက်စေဘဲ Copy/Print ပိတ်ထားသော PDF အဖြစ် ပြောင်းလဲပေးမည်။")

# Sidebar Settings
with st.sidebar:
@@ -36,27 +35,33 @@

    owner_pw = "master_admin_key_123"

def protect_document(pdf_stream, u_pw, o_pw):
    """ဖိုင်ဆိုဒ်ကို အတတ်နိုင်ဆုံး လျှော့ချထားသော Protection Function"""
    doc = fitz.open(stream=pdf_stream, filetype="pdf")
def docx_to_pdf_stream(docx_bytes):
    """Word ဖိုင်ကို Layout မပျက်ဘဲ PDF Stream အဖြစ်ပြောင်းလဲခြင်း"""
    input_stream = io.BytesIO(docx_bytes)
    doc = aw.Document(input_stream)
    
    pdf_output = io.BytesIO()
    # Save as PDF to memory
    doc.save(pdf_output, aw.SaveFormat.PDF)
    return pdf_output.getvalue()

def protect_document(pdf_bytes, u_pw, o_pw):
    """PDF ကို Rasterize လုပ်ပြီး Protection ထည့်သွင်းခြင်း"""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    out_pdf = fitz.open()

    for page in doc:
        # DPI ကို 150 သို့လျှော့ချခြင်း (ဖိုင်ဆိုဒ် သိသိသာသာ သေးသွားစေသည်)
        # DPI 150 provides a good balance of clarity and file size
        pix = page.get_pixmap(dpi=150)
        
        # PNG အစား JPG သုံးပြီး Quality ကို 70% ထားခြင်း (ဆိုဒ်အလွန်သေးသွားစေသည်)
        img_data = pix.tobytes("jpg", jpg_quality=70)

        new_page = out_pdf.new_page(width=page.rect.width, height=page.rect.height)
        new_page.insert_image(page.rect, stream=img_data)

    # Adobe Permissions (Copy=0, Print=0, Edit=0)
    # Permissions: No Copy, No Print, No Edit
    perm = int(fitz.PDF_PERM_ACCESSIBILITY | 0)

    output_buffer = io.BytesIO()
    
    # deflate=True သုံးပြီး PDF ထဲက Data များကို ထပ်မံချုံ့ခြင်း
    out_pdf.save(
        output_buffer,
        encryption=fitz.PDF_ENCRYPT_AES_256,
@@ -70,16 +75,23 @@ def protect_document(pdf_stream, u_pw, o_pw):
    doc.close()
    return output_buffer.getvalue()

uploaded_file = st.file_uploader("ဖိုင်ရွေးချယ်ပါ (PDF, DOCX, XLSX)", type=["pdf", "docx", "xlsx"])
uploaded_file = st.file_uploader("ဖိုင်ရွေးချယ်ပါ (PDF သို့မဟုတ် DOCX)", type=["pdf", "docx"])

if uploaded_file is not None:
    file_ext = uploaded_file.name.split('.')[-1].lower()

    try:
        with st.spinner('လုံခြုံရေးအလွှာများ ထည့်သွင်းပြီး ဖိုင်ဆိုဒ်ကို ချုံ့နေသည်...'):
            # လက်ရှိတွင် PDF processing ကို အခြေခံထားသည်
            # Word/Excel ကို PDF ပြောင်းရန် နည်းပညာအရ PDF stream သို့ အရင်ပို့ရပါမည်
            final_data = protect_document(uploaded_file.read(), user_pw, owner_pw)
        with st.spinner('ဖိုင်ကို Processing လုပ်နေပါသည်...'):
            raw_bytes = uploaded_file.read()
            
            # ၁။ Word ဖြစ်နေလျှင် PDF အရင်ပြောင်း
            if file_ext == "docx":
                pdf_payload = docx_to_pdf_stream(raw_bytes)
            else:
                pdf_payload = raw_bytes

            # ၂။ PDF ကို Security နှင့် Compression ထည့်သွင်း
            final_data = protect_document(pdf_payload, user_pw, owner_pw)

            if final_data:
                st.success(f"✅ အောင်မြင်စွာ လုပ်ဆောင်ပြီးပါပြီ။ (Size: {len(final_data)/1024:.2f} KB)")
@@ -93,4 +105,4 @@ def protect_document(pdf_stream, u_pw, o_pw):
        st.error(f"Error: {e}")

st.divider()
st.caption("Optimized Version: JPG Compression + AES-256 Protection")
st.caption("Feature: DOCX to PDF + Rasterized Compression + AES-256")
