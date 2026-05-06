import streamlit as st
import fitz  # PyMuPDF
import io
from docx import Document
import pandas as pd

# Page setup
st.set_page_config(page_title="Pro Secure Doc Shield", layout="centered")

# --- CSS & JS for UI Protection ---
st.markdown("""
    <style>
    body { -webkit-user-select: none; user-select: none; }
    </style>
    <script>
    document.addEventListener('contextmenu', event => event.preventDefault());
    document.onkeydown = function(e) {
        if (e.ctrlKey && (e.keyCode === 67 || e.keyCode === 86 || e.keyCode === 85 || e.keyCode === 83 || e.keyCode === 80)) {
            return false;
        }
    };
    </script>
    """, unsafe_allow_html=True)

st.title("🛡️ Pro Document Security Shield")
st.info("တင်သမျှဖိုင်များကို မြန်မာစာမပျက်စေဘဲ Copy/Print လုံးဝကူးမရသော PDF အဖြစ် ပြောင်းလဲပေးမည်။")

# Sidebar Settings
with st.sidebar:
    st.header("Security Settings")
    set_password = st.checkbox("Open Password ခံမည်")
    user_pw = ""
    if set_password:
        user_pw = st.text_input("ဖိုင်ဖွင့်ရန် Password", type="password")
    
    # Permission ပြန်ပြင်လိုပါက သုံးရန် Master Key
    owner_pw = "master_admin_key_123"


def protect_document(pdf_stream, u_pw, o_pw):
    """PDF ကို Rasterize လုပ်ပြီး Permission များ ပိတ်ခြင်း (Optimized Size Version)"""
    doc = fitz.open(stream=pdf_stream, filetype="pdf")
    out_pdf = fitz.open()
    
    for page in doc:
        # DPI လျှော့ (150 = size ↓ but still readable)
        pix = page.get_pixmap(dpi=150)

        # Optional: grayscale (လိုရင် uncomment)
        # pix = fitz.Pixmap(fitz.csGRAY, pix)

        # PNG → JPEG (size significantly smaller)
        img_data = pix.tobytes("jpg")

        # Rebuild page as image (no text selection)
        new_page = out_pdf.new_page(width=page.rect.width, height=page.rect.height)
        new_page.insert_image(page.rect, stream=img_data)

    # Permissions (no copy / print / edit)
    perm = int(fitz.PDF_PERM_ACCESSIBILITY | 0)

    output_buffer = io.BytesIO()
    out_pdf.save(
        output_buffer,
        encryption=fitz.PDF_ENCRYPT_AES_256,
        user_pw=u_pw if u_pw else None,
        owner_pw=o_pw,
        permissions=perm,
        garbage=4,      # remove unused objects
        deflate=True,   # compress streams
        clean=True      # optimize structure
    )
    out_pdf.close()
    doc.close()
    return output_buffer.getvalue()


uploaded_file = st.file_uploader("ဖိုင်ရွေးချယ်ပါ (PDF, DOCX, XLSX)", type=["pdf", "docx", "xlsx"])

if uploaded_file is not None:
    file_ext = uploaded_file.name.split('.')[-1].lower()
    
    try:
        with st.spinner('လုံခြုံရေးအလွှာများ ထည့်သွင်းနေသည်...'):
            
            if file_ext == "pdf":
                final_data = protect_document(uploaded_file.read(), user_pw, owner_pw)
            else:
                # NOTE:
                # DOCX/XLSX → PDF conversion not implemented here
                # You must convert to PDF first before processing
                final_data = protect_document(uploaded_file.read(), user_pw, owner_pw)

            if final_data:
                st.success("✅ ဖိုင်ကို အောင်မြင်စွာ ကာကွယ်ပြီးပါပြီ။")
                st.download_button(
                    label="Download Protected PDF",
                    data=final_data,
                    file_name=f"Protected_{uploaded_file.name.split('.')[0]}.pdf",
                    mime="application/pdf"
                )

    except Exception as e:
        st.error(f"Error: {e}")

st.divider()
st.caption("Developed with Streamlit & PyMuPDF (AES-256 Protection, Optimized Compression)")
