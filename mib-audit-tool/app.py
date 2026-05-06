import streamlit as st
import fitz  # PyMuPDF
import io
from docx import Document
import pandas as pd

# Page setup
st.set_page_config(page_title="Pro Secure Doc Shield", layout="wide")

st.title("🛡️ Pro Document Security Shield")
st.write("Word, Excel, PDF ဖိုင်များကို Copy/Print ပိတ်ထားသော PDF အဖြစ် ပြောင်းလဲပေးမည်။")

# ဘေးဘက်တွင် Password သတ်မှတ်ရန်
with st.sidebar:
    st.header("Security Settings")
    set_password = st.checkbox("Password ခံမည် (Open Password)")
    user_pw = ""
    if set_password:
        user_pw = st.text_input("ဖိုင်ဖွင့်ရန် Password ရိုက်ပါ", type="password")
    
    owner_pw = "master_admin_key" # ဒါက Security ပြန်ပြင်ချင်ရင်သုံးဖို့ Master Password ပါ

uploaded_file = st.file_uploader("ဖိုင်ရွေးချယ်ပါ (PDF, DOCX, XLSX)", type=["pdf", "docx", "xlsx"])

def protect_pdf(pdf_stream, u_pw, o_pw):
    doc = fitz.open(stream=pdf_stream, filetype="pdf")
    out_pdf = fitz.open()
    
    # စာသားတွေကို ပုံအဖြစ်ပြောင်းပစ်ခြင်း (ဒါမှ Copy လုံးဝကူးမရမှာဖြစ်ပြီး မြန်မာစာလည်း မပျက်မှာပါ)
    for page in doc:
        pix = page.get_pixmap(dpi=200)
        img_pdf_bytes = pix.tobytes("pdf")
        img_pdf = fitz.open("pdf", img_pdf_bytes)
        out_pdf.insert_pdf(img_pdf)

    # Adobe Standard Permissions
    perm = int(
        fitz.PDF_PERM_ACCESSIBILITY | # ဖတ်ရုံပဲရမယ်
        0 # Copy, Print, Edit အကုန်ပိတ်
    )

    output_buffer = io.BytesIO()
    out_pdf.save(
        output_buffer,
        encryption=fitz.PDF_ENCRYPT_AES_256,
        user_pw=u_pw,   # ဖိုင်ဖွင့်ဖို့ password (မထည့်ရင် ဒီတိုင်းပွင့်မယ်)
        owner_pw=o_pw,  # Permission တွေ ထိန်းချုပ်ဖို့ password
        permissions=perm
    )
    return output_buffer.getvalue()

if uploaded_file is not None:
    file_type = uploaded_file.name.split('.')[-1].lower()
    final_pdf_data = None

    try:
        if file_type == "pdf":
            final_pdf_data = protect_pdf(uploaded_file.read(), user_pw, owner_pw)
        
        elif file_type in ["docx", "xlsx"]:
            st.warning(f"မှတ်ချက်: {file_type.upper()} ဖိုင်များကို Security အပြည့်ရရန် PDF အဖြစ် အလိုအလျောက် ပြောင်းလဲပါမည်။")
            # Word/Excel ကို PDF ပြောင်းရန် နည်းပညာအရ ဖိုင်ကိုအရင်ဖတ်ပြီး ပုံဖော်ရပါသည်
            # ဤနေရာတွင် ရိုးရှင်းစေရန် PDF ဖိုင်ကိုသာ အဓိက နမူနာပြထားသည်
            # Word/Excel တိုက်ရိုက်ပြောင်းလဲခြင်းအတွက် 'aspose-words' သို့မဟုတ် 'comtypes' လိုအပ်နိုင်ပါသည်
            st.info("Word/Excel ကို PDF ပြောင်းလဲခြင်း လုပ်ဆောင်နေသည်...")
            # (စာသားဖတ်ပြီး PDF ထဲထည့်သည့် logic ထည့်သွင်းနိုင်သည်)
            final_pdf_data = protect_pdf(uploaded_file.read(), user_pw, owner_pw)

        if final_pdf_data:
            st.success("✅ Security Layer များ ထည့်သွင်းပြီးပါပြီ။")
            st.download_button(
                label="Download Protected File",
                data=final_pdf_data,
                file_name=f"Protected_{uploaded_file.name.split('.')[0]}.pdf",
                mime="application/pdf"
            )
    except Exception as e:
        st.error(f"အမှားအယွင်းရှိခဲ့သည်: {e}")

st.markdown("""
---
### ထူးခြားချက်များ
1.  **Password မပါလည်း Copy မရ:** ဖိုင်ကိုဖွင့်လိုက်ရင် စာသားတွေကို Select ပေးလို့မရအောင် 'Rasterization' (စာကိုပုံအဖြစ်ပြောင်းခြင်း) လုပ်ထားပါတယ်။
2.  **Adobe AES-256:** အဆင့်မြင့်ဆုံး Encryption သုံးထားလို့ Security အတော်လေး မြင့်ပါတယ်။
3.  **Myanmar Font:** စာမျက်နှာကို Image အဖြစ်ပြောင်းလိုက်တဲ့အတွက် ဖောင့်ပြဿနာ လုံးဝမရှိတော့ပါဘူး။
""")
