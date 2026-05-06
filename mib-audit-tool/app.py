import streamlit as st
import fitz  # PyMuPDF
import io
import aspose.words as aw

# Page setup
st.set_page_config(page_title="Pro Secure Doc Shield", layout="centered")

# --- UI Protection ---
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
st.info("Word သို့မဟုတ် PDF ကို Layout မပျက်စေဘဲ Copy/Print ပိတ်ထားသော PDF အဖြစ် ပြောင်းလဲပေးမည်။")

# Sidebar Settings
with st.sidebar:
    st.header("Security Settings")
    set_password = st.checkbox("Open Password ခံမည်")
    user_pw = ""
    if set_password:
        user_pw = st.text_input("ဖိုင်ဖွင့်ရန် Password", type="password")
    
    owner_pw = "master_admin_key_123"

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
        # DPI 150 provides a good balance of clarity and file size
        pix = page.get_pixmap(dpi=150)
        img_data = pix.tobytes("jpg", jpg_quality=70)
        
        new_page = out_pdf.new_page(width=page.rect.width, height=page.rect.height)
        new_page.insert_image(page.rect, stream=img_data)

    # Permissions: No Copy, No Print, No Edit
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
    
    out_pdf.close()
    doc.close()
    return output_buffer.getvalue()

uploaded_file = st.file_uploader("ဖိုင်ရွေးချယ်ပါ (PDF သို့မဟုတ် DOCX)", type=["pdf", "docx"])

if uploaded_file is not None:
    file_ext = uploaded_file.name.split('.')[-1].lower()
    
    try:
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
                st.download_button(
                    label="Download Protected PDF",
                    data=final_data,
                    file_name=f"Protected_{uploaded_file.name.split('.')[0]}.pdf",
                    mime="application/pdf"
                )
    except Exception as e:
        st.error(f"Error: {e}")

st.divider()
st.caption("Feature: DOCX to PDF + Rasterized Compression + AES-256")
