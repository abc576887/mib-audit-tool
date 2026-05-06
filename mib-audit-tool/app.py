import streamlit as st
import fitz  # PyMuPDF
import io

# Page setup
st.set_page_config(page_title="Secure Image-PDF Shield", layout="centered")

# --- UI Protection (Selection & Right-click ပိတ်ခြင်း) ---
st.markdown("""
    <style> body { -webkit-user-select: none; user-select: none; } </style>
    <script> document.addEventListener('contextmenu', event => event.preventDefault()); </script>
    """, unsafe_allow_html=True)

st.title("🛡️ Image-PDF Shield (Password Protected)")
st.info("စာသားကူးမရသော ပုံရိပ် PDF ပြောင်းပေးမည်ဖြစ်ပြီး ဖိုင်ဖွင့်ရန် Password ပါ သတ်မှတ်နိုင်ပါသည်။")

# Sidebar Settings
with st.sidebar:
    st.header("Security Settings")
    use_password = st.checkbox("Open Password သတ်မှတ်မည်")
    user_pw = ""
    if use_password:
        user_pw = st.text_input("ဖိုင်ဖွင့်ရန် Password ရိုက်ပါ", type="password", placeholder="ဥပမာ - 123456")
    
    st.divider()
    owner_pw = "master_key_999" # Permission ပြန်ပြင်လိုလျှင်သုံးရန် (Internal use)

def process_to_secure_pdf(file_bytes, u_pw, o_pw):
    """PDF ကို Rasterize လုပ်ပြီး Password နှင့် Permissions များ ထည့်သွင်းခြင်း"""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    out_pdf = fitz.open()
    
    for page in doc:
        # DPI 120 + JPG Quality 60 (ဖိုင်ဆိုဒ် သိသိသာသာ သေးစေရန်)
        pix = page.get_pixmap(dpi=120)
        img_data = pix.tobytes("jpg", jpg_quality=60)
        
        # စာမျက်နှာအသစ်ပေါ်သို့ ပုံပြန်တင်ခြင်း
        new_page = out_pdf.new_page(width=page.rect.width, height=page.rect.height)
        new_page.insert_image(page.rect, stream=img_data)

    # Permissions (Copy=0, Print=0, Edit=0)
    perm = int(fitz.PDF_PERM_ACCESSIBILITY | 0)

    output_buffer = io.BytesIO()
    
    # Password နှင့် Encryption ထည့်သွင်းခြင်း
    out_pdf.save(
        output_buffer,
        encryption=fitz.PDF_ENCRYPT_AES_256,
        user_pw=u_pw if u_pw else None,  # ဖိုင်ဖွင့်ရန် Password
        owner_pw=o_pw,                   # Permission များ ပြင်ရန် Master Password
        permissions=perm,
        deflate=True                     # ဖိုင်ဆိုဒ်ကို ထပ်မံချုံ့ခြင်း
    )
    
    doc.close()
    out_pdf.close()
    return output_buffer.getvalue()

uploaded_file = st.file_uploader("PDF ဖိုင်တင်ပါ", type=["pdf"])

if uploaded_file:
    if st.button("Generate Secure File"):
        with st.spinner('လုံခြုံရေးအလွှာများ ထည့်သွင်းနေသည်...'):
            try:
                final_pdf = process_to_secure_pdf(uploaded_file.read(), user_pw, owner_pw)
                
                st.success(f"✅ လုပ်ဆောင်ပြီးပါပြီ။ ဖိုင်ဆိုဒ်: {len(final_pdf)/1024:.1f} KB")
                
                st.download_button(
                    label="📥 Download Protected PDF",
                    data=final_pdf,
                    file_name=f"Secure_{uploaded_file.name}",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("""
---
