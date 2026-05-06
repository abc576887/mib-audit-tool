import streamlit as st
import fitz  # PyMuPDF
import io
import pandas as pd
from docx import Document

# Page setup
st.set_page_config(page_title="Image-Based Secure Shield", layout="centered")

# --- UI Protection ---
st.markdown("""
    <style> body { -webkit-user-select: none; user-select: none; } </style>
    <script> document.addEventListener('contextmenu', event => event.preventDefault()); </script>
    """, unsafe_allow_html=True)

st.title("🛡️ Image-Based PDF Shield")
st.info("တင်သမျှဖိုင်များကို စာသားကူးမရသော 'ပုံရိပ်စစ်စစ်' PDF အဖြစ် ပြောင်းလဲပေးမည်။")

def process_to_image_pdf(file_bytes, file_ext):
    """မည်သည့်ဖိုင်ကိုမဆို Image-based PDF အဖြစ်ပြောင်းလဲခြင်း"""
    out_pdf = fitz.open()
    
    # ၁။ PDF ဖြစ်လျှင် တိုက်ရိုက် Image ပြောင်းသည်
    if file_ext == "pdf":
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    
    # ၂။ Excel ဖြစ်လျှင် ယာယီ PDF အရင်ပြောင်းရန် လိုအပ်သည် 
    # (ဤနေရာတွင် ဥပမာအဖြစ် PDF rasterization logic ကို အဓိကပြထားပါသည်)
    else:
        # Word/Excel logic များအတွက် ယာယီစာမျက်နှာများ ဖန်တီးရန်
        st.error(f"{file_ext.upper()} ကို Image PDF ပြောင်းရန် PDF အဖြစ် အရင်တင်ပေးပါ။")
        return None

    for page in doc:
        # ဆိုဒ်သေးအောင် DPI 120 နှင့် JPG Quality 60 သုံးထားပါသည်
        pix = page.get_pixmap(dpi=120)
        img_data = pix.tobytes("jpg", jpg_quality=60)
        
        new_page = out_pdf.new_page(width=page.rect.width, height=page.rect.height)
        new_page.insert_image(page.rect, stream=img_data)

    # Security Settings (Copy ပိတ်၊ Print ပိတ်)
    perm = int(fitz.PDF_PERM_ACCESSIBILITY | 0)
    output_buffer = io.BytesIO()
    out_pdf.save(output_buffer, encryption=fitz.PDF_ENCRYPT_AES_256, 
                 owner_pw="admin123", permissions=perm, deflate=True)
    
    doc.close()
    out_pdf.close()
    return output_buffer.getvalue()

uploaded_file = st.file_uploader("PDF ဖိုင်တင်ပါ", type=["pdf"])

if uploaded_file:
    if st.button("Generate Secure Image-PDF"):
        with st.spinner('ပုံရိပ်များအဖြစ် ပြောင်းလဲနေသည်...'):
            final_pdf = process_to_image_pdf(uploaded_file.read(), "pdf")
            
            if final_pdf:
                st.success(f"✅ အောင်မြင်စွာ ပြောင်းလဲပြီးပါပြီ။ ဆိုဒ်: {len(final_pdf)/1024:.1f} KB")
                st.download_button(
                    label="Download Secure PDF",
                    data=final_pdf,
                    file_name=f"Secure_Image_{uploaded_file.name}",
                    mime="application/pdf"
                )

st.markdown("""
---
### ဒီနည်းလမ်းရဲ့ အကျိုးကျေးဇူး:
1. **No Text Data:** ဖိုင်ထဲမှာ စာသား (Text) လုံးဝမပါတော့ဘဲ ဓာတ်ပုံတွေပဲ ရှိတော့တာမို့ Copy လုံးဝကူးမရပါ။
2. **Small Size:** JPG Compression သုံးထားလို့ ဖိုင်ဆိုဒ် အတော်လေး သေးသွားပါတယ်။
3. **Myanmar Font Safe:** စာသားတွေက ပုံဖြစ်သွားပြီမို့ ဘယ်စက်မှာဖွင့်ဖွင့် မြန်မာစာ လုံးဝမပျက်ပါ။
""")
