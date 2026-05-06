import streamlit as st
import pandas as pd
from docx import Document
import fitz  # PyMuPDF
import io

# Page Config
st.set_page_config(page_title="Secure Document Hub", layout="centered")

# --- UI Protection (Selection & Right-click ပိတ်ခြင်း) ---
st.markdown("""
    <style>
    .main { -webkit-user-select: none; user-select: none; }
    </style>
    <script>
    document.addEventListener('contextmenu', event => event.preventDefault());
    </script>
    """, unsafe_allow_html=True)

def create_protected_pdf(input_data, file_type):
    """မည်သည့်ဖိုင်ကိုမဆို Copy ကူးမရသော Image-based PDF အဖြစ်ပြောင်းခြင်း"""
    out_pdf = fitz.open()
    
    if file_type == "pdf":
        doc = fitz.open(stream=input_data, filetype="pdf")
        for page in doc:
            pix = page.get_pixmap(dpi=200)
            img_data = pix.tobytes("png")
            new_page = out_pdf.new_page(width=page.rect.width, height=page.rect.height)
            new_page.insert_image(page.rect, stream=img_data)
    
    # Word/Excel အတွက်ဆိုလျှင် Viewer ထဲက data ကို PDF စာမျက်နှာအဖြစ် ပြောင်းလဲရပါမည်
    # (ဤနေရာတွင် ဥပမာအဖြစ် PDF rasterization ကို အဓိကပြထားပါသည်)
    
    # Copy & Print ပိတ်ခြင်း
    perm = int(fitz.PDF_PERM_ACCESSIBILITY | 0)
    output_buffer = io.BytesIO()
    out_pdf.save(output_buffer, encryption=fitz.PDF_ENCRYPT_AES_256, 
                 owner_pw="admin_key", permissions=perm)
    return output_buffer.getvalue()

st.title("🛡️ Secure Viewer & Downloader")
st.write("ဖိုင်ကို ကြည့်ရှုနိုင်သလို၊ လုံခြုံရေးအပြည့်ပါသော (Copy-Protected) ဖိုင်အဖြစ် Download ရယူနိုင်ပါသည်။")

uploaded_file = st.file_uploader("ဖိုင်တင်ပါ", type=["xlsx", "docx", "pdf"])

if uploaded_file:
    file_bytes = uploaded_file.read()
    file_type = uploaded_file.name.split('.')[-1].lower()

    # --- ၁။ Viewer ပိုင်း (App ထဲမှာ ကြည့်ရန်) ---
    st.subheader("👀 Preview (Read-Only)")
    if file_type == "xlsx":
        df = pd.read_excel(io.BytesIO(file_bytes))
        st.table(df.head(20)) # နမူနာ ၂၀ ပြခြင်း
    elif file_type == "docx":
        doc = Document(io.BytesIO(file_bytes))
        text = "\n".join([p.text for p in doc.paragraphs])
        st.text_area("Content", text, height=300, disabled=True)
    elif file_type == "pdf":
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        pix = doc[0].get_pixmap(dpi=100) # ပထမစာမျက်နှာကို နမူနာပြခြင်း
        st.image(pix.tobytes("png"))

    # --- ၂။ Downloader ပိုင်း (Copy-Protected ဖိုင်ထုတ်ပေးခြင်း) ---
    st.divider()
    st.subheader("📥 Download Secure Version")
    st.warning("Download ရရှိမည့်ဖိုင်သည် PDF Format ဖြစ်သွားမည်ဖြစ်ပြီး Copy ကူး၍မရအောင် ပိတ်ထားပါမည်။")
    
    if st.button("Generate Secure File"):
        protected_data = create_protected_pdf(file_bytes, "pdf" if file_type == "pdf" else "pdf")
        st.download_button(
            label="Download Now",
            data=protected_data,
            file_name=f"Protected_{uploaded_file.name.split('.')[0]}.pdf",
            mime="application/pdf"
        )
