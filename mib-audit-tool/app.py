import streamlit as st
import fitz  # PyMuPDF
import io

# Page setup
st.set_page_config(page_title="Pro Secure Shield", layout="centered")

# --- UI Protection (Copy/Right-click ပိတ်ခြင်း) ---
st.markdown("""
    <style> body { -webkit-user-select: none; user-select: none; } </style>
    <script> document.addEventListener('contextmenu', event => event.preventDefault()); </script>
""", unsafe_allow_html=True)

st.title("🛡️ Secure Image-PDF Shield")
st.info("Layout လုံးဝမပျက်စေရန်အတွက် Word/Excel ဖိုင်များကို PDF အဖြစ် Save ပြီးမှ ဤနေရာတွင် တင်ပေးပါ။")

# Sidebar
with st.sidebar:
    st.header("Security Settings")
    use_password = st.checkbox("Open Password သတ်မှတ်မည်")
    user_pw = st.text_input("Password", type="password") if use_password else ""
    st.divider()
    owner_pw = "master_key_999"

def finalize_to_image_pdf(pdf_stream, u_pw, o_pw):
    """Layout ကို ၁၀၀% ထိန်းသိမ်းပြီး Image-based PDF သို့ ပြောင်းလဲခြင်း"""
    doc = fitz.open(stream=pdf_stream, filetype="pdf")
    out_pdf = fitz.open()
    
    for page in doc:
        # DPI 150 က စာဖတ်ရတာ ကြည်လင်ပြီး ဖိုင်ဆိုဒ်ကို သင့်တင့်စေပါတယ်
        pix = page.get_pixmap(dpi=150)
        
        # PNG အစား JPG (Quality 75) သုံးခြင်းက Layout မပျက်ဘဲ ဖိုင်ဆိုဒ်ကို သိသိသာသာ သေးစေပါတယ်
        img_data = pix.tobytes("jpg", jpg_quality=75)
        
        new_page = out_pdf.new_page(width=page.rect.width, height=page.rect.height)
        new_page.insert_image(page.rect, stream=img_data)

    # Permissions Setting (Copy=0, Print=0, Edit=0)
    perm = int(fitz.PDF_PERM_ACCESSIBILITY | 0)
    
    output_buffer = io.BytesIO()
    out_pdf.save(
        output_buffer,
        encryption=fitz.PDF_ENCRYPT_AES_256,
        user_pw=u_pw if u_pw else None,
        owner_pw=o_pw,
        permissions=perm,
        deflate=True # ဖိုင်ဆိုဒ်ထပ်ချုံ့ရန်
    )
    doc.close()
    out_pdf.close()
    return output_buffer.getvalue()

uploaded_file = st.file_uploader("PDF ဖိုင်တင်ပါ (Word/Excel ကို PDF အဖြစ် Save ပြီးမှ တင်ပါ)", type=["pdf"])

if uploaded_file:
    if st.button("Generate Secure File"):
        with st.spinner('လုံခြုံရေးအတွက် လုပ်ဆောင်နေသည်...'):
            try:
                # PDF မူရင်း Layout အတိုင်း Image ပြောင်းလဲခြင်း
                final_pdf = finalize_to_image_pdf(uploaded_file.read(), user_pw, owner_pw)
                
                st.success(f"✅ လုပ်ဆောင်ပြီးပါပြီ။ ဖိုင်ဆိုဒ်: {len(final_pdf)/1024:.1f} KB")
                st.download_button(
                    label="📥 Download Secure PDF",
                    data=final_pdf,
                    file_name=f"Secure_{uploaded_file.name}",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("""
---
### 💡 အရေးကြီးသော လမ်းညွှန်ချက်
Word သို့မဟုတ် Excel ဖိုင်များကို ဤ App ထဲတင်လျှင် **Layout ပျက်ခြင်းမှ ကာကွယ်ရန်** အောက်ပါအတိုင်း လုပ်ဆောင်ပါ-
1. သင်၏ Word/Excel ဖိုင်တွင် **File > Save As > PDF** ကို နှိပ်၍ PDF အဖြစ် အရင်ပြောင်းပါ။
2. ရလာသော PDF ကို ဤ App ထဲသို့ တင်ပါ။
3. App က ၎င်း PDF ကို Layout လုံးဝမပျက်စေဘဲ **စာသားကူးမရသော Image PDF** အဖြစ် ပြောင်းလဲပေးပါလိမ့်မည်။
""")
