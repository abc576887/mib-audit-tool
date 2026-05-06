import streamlit as st
import fitz  # PyMuPDF
import io
from docx import Document
import pandas as pd

# Page setup
st.set_page_config(page_title="Pro Secure Doc Shield", layout="centered")

# --- UI Protection (Right-click & Selection ပိတ်ခြင်း) ---
st.markdown("""
    <style>
    body { -webkit-user-select: none; user-select: none; }
    .stApp { pointer-events: auto; }
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
st.info("ဖိုင်ဆိုဒ်ကို ချုံ့ပေးထားပြီး Copy/Print ပိတ်ထားသော PDF အဖြစ် ပြောင်းလဲပေးမည်။")

# Sidebar Settings
with st.sidebar:
    st.header("Security Settings")
    set_password = st.checkbox("Open Password ခံမည်")
    user_pw = ""
    if set_password:
        user_pw = st.text_input("ဖိုင်ဖွင့်ရန် Password", type="password")
    
    owner_pw = "master_admin_key_123"

def protect_document(pdf_stream, u_pw, o_pw):
    """ဖိုင်ဆိုဒ်ကို အတတ်နိုင်ဆုံး လျှော့ချထားသော Protection Function"""
    doc = fitz.open(stream=pdf_stream, filetype="pdf")
    out_pdf = fitz.open()
    
    for page in doc:
        # DPI ကို 150 သို့လျှော့ချခြင်း (ဖိုင်ဆိုဒ် သိသိသာသာ သေးသွားစေသည်)
        pix = page.get_pixmap(dpi=150)
        
        # PNG အစား JPG သုံးပြီး Quality ကို 70% ထားခြင်း (ဆိုဒ်အလွန်သေးသွားစေသည်)
        img_data = pix.tobytes("jpg", jpg_quality=70)
        
        new_page = out_pdf.new_page(width=page.rect.width, height=page.rect.height)
        new_page.insert_image(page.rect, stream=img_data)

    # Adobe Permissions (Copy=0, Print=0, Edit=0)
    perm = int(fitz.PDF_PERM_ACCESSIBILITY | 0)

    output_buffer = io.BytesIO()
    
    # deflate=True သုံးပြီး PDF ထဲက Data များကို ထပ်မံချုံ့ခြင်း
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
    
    try:
        with st.spinner('လုံခြုံရေးအလွှာများ ထည့်သွင်းပြီး ဖိုင်ဆိုဒ်ကို ချုံ့နေသည်...'):
            # လက်ရှိတွင် PDF processing ကို အခြေခံထားသည်
            # Word/Excel ကို PDF ပြောင်းရန် နည်းပညာအရ PDF stream သို့ အရင်ပို့ရပါမည်
            final_data = protect_document(uploaded_file.read(), user_pw, owner_pw)

            if final_data:
                st.success(f"✅ အောင်မြင်စွာ လုပ်ဆောင်ပြီးပါပြီ။ (Size: {len(final_data)/1024:.2f} KB)")
                st.download_button(
                    label="Download Protected PDF",
                    data=final_data,
                    file_name=f"Protected_{uploaded_file.name.split('.')[0]}.pdf",
                    mime="application/pdf"
                )
    except Exception as e:
        st.error(f"Error: {e}")

st.divider()
st.caption("Optimized Version: JPG Compression + AES-256 Protection")
