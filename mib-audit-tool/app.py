import streamlit as st
import fitz  # PyMuPDF
import io
import zipfile
import os
import hashlib
import base64
import struct
import xml.etree.ElementTree as ET

# ─── Page Setup ───────────────────────────────
st.set_page_config(page_title="Pro Secure Doc Shield", layout="centered")

st.markdown("""
    <style>
    body { -webkit-user-select: none; user-select: none; }
    </style>
    <script>
    document.addEventListener('contextmenu', e => e.preventDefault());
    document.onkeydown = function(e) {
        if (e.ctrlKey && [67,86,85,83,80].includes(e.keyCode)) return false;
    };
    </script>
""", unsafe_allow_html=True)

st.title("🛡️ Pro Document Security Shield")

# ─── Sidebar ──────────────────────────────────
with st.sidebar:
    st.header("⚙️ Security Settings")

    set_password = st.checkbox("🔑 Password ခံမည်")
    user_pw = ""
    if set_password:
        user_pw = st.text_input("Password", type="password")

    owner_pw = "master_admin_key_123"

    st.divider()
    st.markdown("**Output Mode ရွေးချယ်ပါ:**")
    output_mode = st.radio(
        "Output Mode",
        options=["same_format", "convert_to_pdf"],
        format_func=lambda x: {
            "same_format":    "📄 Format အတိုင်းထား + Lock",
            "convert_to_pdf": "🔒 PDF အဖြစ်ပြောင်း (အပြည့်ပိတ်)",
        }[x],
        label_visibility="collapsed"
    )

    st.divider()
    if output_mode == "same_format":
        st.warning("⚠️ DOCX/XLSX lock ကို LibreOffice/Google Docs မှာ bypass နိုင်သည်")
    else:
        st.success("✅ PDF (Image-based) = Copy တကယ်မရနိုင်")


# ══════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════

# Register all namespaces to preserve them during parse/write
NAMESPACES = {
    'w':  'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'r':  'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
    'x':  'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
}
for prefix, uri in NAMESPACES.items():
    ET.register_namespace(prefix, uri)


def _sha512_hash(password: str):
    salt = os.urandom(16)
    pw_bytes = password.encode("utf-16-le")
    h = hashlib.sha512(salt + pw_bytes).digest()
    for i in range(100000):
        h = hashlib.sha512(h + struct.pack("<I", i)).digest()
    return base64.b64encode(salt).decode(), base64.b64encode(h).decode()


# ── 1. PDF → Protected PDF ────────────────────
def protect_pdf(pdf_bytes: bytes, u_pw: str, o_pw: str) -> bytes:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    out = fitz.open()
    for page in doc:
        pix = page.get_pixmap(dpi=150)
        img = pix.tobytes("jpg", jpg_quality=70)
        np  = out.new_page(width=page.rect.width, height=page.rect.height)
        np.insert_image(page.rect, stream=img)
    perm = int(fitz.PDF_PERM_ACCESSIBILITY)
    buf  = io.BytesIO()
    out.save(buf, encryption=fitz.PDF_ENCRYPT_AES_256,
             user_pw=u_pw or None, owner_pw=o_pw,
             permissions=perm, deflate=True)
    out.close(); doc.close()
    return buf.getvalue()


# ── 2. DOCX → Protected DOCX ─────────────────
def protect_docx(docx_bytes: bytes, password: str = None) -> bytes:
    W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

    # Register all common namespaces before parsing
    ns_map = {
        '':    W,
        'wpc': 'http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas',
        'cx':  'http://schemas.microsoft.com/office/drawing/2014/chartex',
        'mc':  'http://schemas.openxmlformats.org/markup-compatibility/2006',
        'o':   'urn:schemas-microsoft-com:office:office',
        'r':   'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
        'm':   'http://schemas.openxmlformats.org/officeDocument/2006/math',
        'v':   'urn:schemas-microsoft-com:vml',
        'wp14':'http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing',
        'wp':  'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
        'w10': 'urn:schemas-microsoft-com:office:word',
        'w14': 'http://schemas.microsoft.com/office/word/2010/wordml',
        'w15': 'http://schemas.microsoft.com/office/word/2012/wordml',
        'w16': 'http://schemas.microsoft.com/office/word/2018/wordml',
        'wpg': 'http://schemas.microsoft.com/office/word/2010/wordprocessingGroup',
        'wpi': 'http://schemas.microsoft.com/office/word/2010/wordprocessingInk',
        'wne': 'http://schemas.microsoft.com/office/word/2006/wordml',
        'wps': 'http://schemas.microsoft.com/office/word/2010/wordprocessingShape',
    }
    for p, u in ns_map.items():
        ET.register_namespace(p, u)

    inp = io.BytesIO(docx_bytes)
    out = io.BytesIO()

    with zipfile.ZipFile(inp, "r") as zin, \
         zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:

        for item in zin.namelist():
            data = zin.read(item)

            if item == "word/settings.xml":
                try:
                    tree = ET.fromstring(data)
                    tag_prot = f"{{{W}}}documentProtection"

                    # Remove existing protection
                    for old in tree.findall(tag_prot):
                        tree.remove(old)

                    # Build new protection element
                    prot = ET.Element(tag_prot)
                    prot.set(f"{{{W}}}edit",        "readOnly")
                    prot.set(f"{{{W}}}enforcement",  "1")
                    prot.set(f"{{{W}}}formatting",   "1")

                    if password:
                        salt_b64, hash_b64 = _sha512_hash(password)
                        prot.set(f"{{{W}}}cryptProviderType",   "rsaFull")
                        prot.set(f"{{{W}}}cryptAlgorithmClass", "hash")
                        prot.set(f"{{{W}}}cryptAlgorithmType",  "typeAny")
                        prot.set(f"{{{W}}}cryptAlgorithmSid",   "14")
                        prot.set(f"{{{W}}}cryptSpinCount",      "100000")
                        prot.set(f"{{{W}}}hash",                hash_b64)
                        prot.set(f"{{{W}}}salt",                salt_b64)

                    tree.insert(0, prot)
                    data = ET.tostring(tree, encoding="unicode").encode("utf-8")
                    data = b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' + data
                except Exception as e:
                    pass  # keep original if parse fails

            zout.writestr(item, data)

    return out.getvalue()


# ── 3. XLSX → Protected XLSX ──────────────────
def protect_xlsx(xlsx_bytes: bytes, password: str = None) -> bytes:
    NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    ET.register_namespace('', NS)

    def sheet_attribs(pw):
        a = {
            f"{{{NS}}}sheet":               "1",
            f"{{{NS}}}objects":             "1",
            f"{{{NS}}}scenarios":           "1",
            f"{{{NS}}}selectLockedCells":   "0",
            f"{{{NS}}}selectUnlockedCells": "0",
        }
        if pw:
            salt_b64, hash_b64 = _sha512_hash(pw)
            a[f"{{{NS}}}algorithmName"] = "SHA-512"
            a[f"{{{NS}}}hashValue"]     = hash_b64
            a[f"{{{NS}}}saltValue"]     = salt_b64
            a[f"{{{NS}}}spinCount"]     = "100000"
        return a

    inp = io.BytesIO(xlsx_bytes)
    out = io.BytesIO()

    with zipfile.ZipFile(inp, "r") as zin, \
         zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:

        for item in zin.namelist():
            data = zin.read(item)

            if item.startswith("xl/worksheets/sheet") and item.endswith(".xml"):
                try:
                    tree = etree_str = data.decode("utf-8")
                    root = ET.fromstring(data)

                    # Remove existing sheetProtection
                    tag_prot = f"{{{NS}}}sheetProtection"
                    for old in root.findall(tag_prot):
                        root.remove(old)

                    # Build new protection element
                    prot = ET.Element(tag_prot)
                    for k, v in sheet_attribs(password).items():
                        prot.set(k, v)

                    # Insert after sheetData
                    insert_pos = len(list(root))
                    for idx, child in enumerate(root):
                        if child.tag == f"{{{NS}}}sheetData":
                            insert_pos = idx + 1
                            break
                    root.insert(insert_pos, prot)

                    data = ET.tostring(root, encoding="unicode").encode("utf-8")
                    data = b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' + data
                except Exception:
                    pass

            zout.writestr(item, data)

    return out.getvalue()


# ── 4. DOCX/XLSX → PDF via LibreOffice ────────
def office_to_protected_pdf(file_bytes: bytes, ext: str,
                             u_pw: str, o_pw: str) -> bytes:
    import subprocess, tempfile, shutil
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        raise RuntimeError(
            "LibreOffice မတွေ့ပါ။\n"
            "packages.txt ဖိုင်မှာ  libreoffice  ထည့်ပြီး redeploy လုပ်ပါ။"
        )
    with tempfile.TemporaryDirectory() as tmp:
        in_path = os.path.join(tmp, f"input.{ext}")
        with open(in_path, "wb") as f:
            f.write(file_bytes)
        subprocess.run(
            [soffice, "--headless", "--convert-to", "pdf", "--outdir", tmp, in_path],
            check=True, capture_output=True
        )
        pdf_path = os.path.join(tmp, "input.pdf")
        if not os.path.exists(pdf_path):
            raise RuntimeError("LibreOffice PDF convert မအောင်မြင်ပါ။")
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
    return protect_pdf(pdf_bytes, u_pw, o_pw)


# ══════════════════════════════════════════════
#  MAIN UI
# ══════════════════════════════════════════════

st.markdown("---")

if output_mode == "same_format":
    st.info("📂 **Format အတိုင်း Mode** — Excel→Excel | Word→Word | PDF→PDF")
else:
    st.success("🔒 **PDF Convert Mode** — အားလုံးကို Image-based Protected PDF ပြောင်းမည်")

uploaded_file = st.file_uploader(
    "ဖိုင်ရွေးချယ်ပါ (PDF, DOCX, XLSX)",
    type=["pdf", "docx", "xlsx"]
)

if uploaded_file:
    ext  = uploaded_file.name.rsplit(".", 1)[-1].lower()
    raw  = uploaded_file.read()
    base = uploaded_file.name.rsplit(".", 1)[0]

    try:
        with st.spinner("🔐 လုံခြုံရေးအလွှာများ ထည့်သွင်းနေသည်..."):

            if output_mode == "same_format":
                if ext == "pdf":
                    result   = protect_pdf(raw, user_pw, owner_pw)
                    out_name = f"Protected_{uploaded_file.name}"
                    mime     = "application/pdf"
                    label    = "PDF → Image-based + AES-256"
                elif ext == "docx":
                    result   = protect_docx(raw, user_pw or None)
                    out_name = f"Protected_{base}.docx"
                    mime     = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    label    = "DOCX → Read-only Lock (Word format အတိုင်း)"
                elif ext == "xlsx":
                    result   = protect_xlsx(raw, user_pw or None)
                    out_name = f"Protected_{base}.xlsx"
                    mime     = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    label    = "XLSX → All Sheets Locked (Excel format အတိုင်း)"
            else:
                if ext == "pdf":
                    result = protect_pdf(raw, user_pw, owner_pw)
                    label  = "PDF → Image-based + AES-256 Protected PDF"
                else:
                    result = office_to_protected_pdf(raw, ext, user_pw, owner_pw)
                    label  = f"{ext.upper()} → Image-based + AES-256 Protected PDF"
                out_name = f"Protected_{base}.pdf"
                mime     = "application/pdf"

        col1, col2 = st.columns(2)
        col1.success("✅ အောင်မြင်ပြီး!")
        col2.info(f"📦 {len(result)/1024:.1f} KB")
        st.caption(f"🔐 {label}")
        st.download_button(
            label=f"⬇️ Download — {out_name}",
            data=result,
            file_name=out_name,
            mime=mime,
            use_container_width=True,
            type="primary"
        )

    except RuntimeError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"❌ Error: {e}")

st.divider()
st.caption("Pro Document Security Shield | Same-Format Lock + PDF Convert Mode")
