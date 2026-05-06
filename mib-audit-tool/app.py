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
    owner_pw = "master_key_999"

def process_to_secure_pdf(file_bytes, u_pw, o_pw):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    out_pdf = fitz.open()
    
    for page in doc:
        # DPI 120 + JPG Quality 60 (ဆိုဒ်ချုံ့ရန်)
        pix = page.get_pixmap(dpi=120)
        img_data = pix.tobytes("jpg", jpg_quality=60)
        
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
### ဤဖိုင်၏ ထူးခြားချက်များ-
* **Image-Based:** စာသားများကို ပုံရိပ်အဖြစ် ပြောင်းလဲထား၍ Copy ကူး၍ လုံးဝမရပါ။
* **Password Protected:** Password မှန်မှသာ ဖိုင်ကို ဖွင့်ကြည့်နိုင်ပါမည်။
* **Compression:** JPG Quality 60% ဖြင့် ဖိုင်ဆိုဒ်ကို လျှော့ချပေးထားပါသည်။
""")
