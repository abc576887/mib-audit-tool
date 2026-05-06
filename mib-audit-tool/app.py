import streamlit as st
import fitz  # PyMuPDF
import io
import os
import pandas as pd
from docx import Document

# Page setup
st.set_page_config(page_title="Universal Secure PDF", layout="centered")

# --- UI Protection (Selection & Right-click ပိတ်ခြင်း) ---
st.markdown("""
    <style> body { -webkit-user-select: none; user-select: none; } </style>
    <script> document.addEventListener('contextmenu', event => event.preventDefault()); </script>
""", unsafe_allow_html=True)

st.title("🛡️ Universal Secure PDF Shield")
st.info("တင်သမျှဖိုင်ကို Copy ကူးမရသော Image-PDF အဖြစ် ပြောင်းလဲပေးမည်။")

# Sidebar
with st.sidebar:
    st.header("Security Settings")
    set_pw = st.checkbox("Password ခံမည်")
    user_pw = st.text_input("Password ရိုက်ပါ", type="password") if set_pw else ""
    owner_pw = "master_admin_key"

def finalize_to_image_pdf(pdf_stream, u_pw, o_pw):
    """Layout မပျက်စေဘဲ Image PDF ပြောင်းလဲပြီး ဆိုဒ်ချုံ့ခြင်း"""
    doc = fitz.open(stream=pdf_stream, filetype="pdf")
    out_pdf = fitz.open()
    
    for page in doc:
        # DPI 150 + JPG Quality 70 (ဖတ်လို့ကြည်ပြီး ဆိုဒ်သေးစေရန်)
        pix = page.get_pixmap(dpi=150)
        img_data = pix.tobytes("jpg", jpg_quality=70)
        
        new_page = out_pdf.new_page(width=page.rect.width, height=page.rect.height)
        new_page.insert_image(page.rect, stream=img_data)

    perm = int(fitz.PDF_PERM_ACCESSIBILITY | 0) # Copy/Print ပိတ်
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

uploaded_file = st.file_uploader("ဖိုင်ရွေးပါ (PDF, Word, Excel)", type=["pdf", "docx", "xlsx"])

if uploaded_file:
    file_ext = uploaded_file.name.split('.')[-1].lower()
    
    if st.button("Generate Secure Image-PDF"):
        try:
            with st.spinner('Converting... (Layout မပျက်စေရန် လုပ်ဆောင်နေပါသည်)'):
                
                # ၁။ PDF တိုက်ရိုက်တင်လျှင်
                if file_ext == "pdf":
                    pdf_input = uploaded_file.read()
                
                # ၂။ Word/Excel တင်လျှင် (Layout မပျက်စေရန် အသိပေးချက်)
                else:
                    st.warning(f"{file_ext.upper()} ဖိုင်များအတွက် Layout ၁၀၀% တိကျစေရန် PDF အဖြစ် Save ပြီးမှ တင်ပေးပါရန် အကြံပြုပါသည်။")
                    # အောက်ပါတို့သည် ရိုးရှင်းသော conversion များအတွက်သာဖြစ်သည်
                    if file_ext == "xlsx":
                        # Excel to PDF logic (Simplified)
                        df = pd.read_excel(uploaded_file)
                        st.write("Excel Data Preview:", df.head())
                        st.error("Excel ကို PDF အဖြစ် အရင်ပြောင်းပြီးမှ တင်ပေးပါ။")
                        st.stop()
                    elif file_ext == "docx":
                        st.error("Word ကို PDF အဖြစ် အရင်ပြောင်းပြီးမှ တင်ပေးပါ။")
                        st.stop()

                # ၃။ အပြီးသတ် Image-based PDF ပြောင်းလဲခြင်း
                final_data = finalize_to_image_pdf(pdf_input, user_pw, owner_pw)
                
                st.success(f"✅ လုပ်ဆောင်ပြီးပါပြီ။ (Size: {len(final_data)/1024:.1f} KB)")
                st.download_button(
                    label="📥 Download Secure PDF",
                    data=final_data,
                    file_name=f"Secure_{uploaded_file.name.split('.')[0]}.pdf",
                    mime="application/pdf"
                )
        except Exception as e:
            st.error(f"Error: {e}")

st.markdown("""
---
### 💡 ဘာကြောင့် PDF အရင်ပြောင်းခိုင်းတာလဲ?
* **Layout ၁၀၀% မှန်စေရန်:** Word/Excel ကို App ထဲမှာ တိုက်ရိုက်ပြောင်းရင် မြန်မာစာနဲ့ ဇယားကွက်တွေ ပျက်တတ်ပါတယ်။ Microsoft Office ထဲမှာ **Save As PDF** လုပ်တာက အကောင်းဆုံးပါ။
* **Copy လုံးဝမရခြင်း:** App က ရလာတဲ့ PDF ကို Image PDF အဖြစ် ထပ်မံပြောင်းလဲပေးတဲ့အတွက် ဘယ်သူမှ Copy ကူးလို့ မရတော့ပါဘူး။
""")
