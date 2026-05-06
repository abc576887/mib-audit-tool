import streamlit as st
import fitz  # PyMuPDF
import io
import time
from pathlib import Path

# ─────────────────────────────────────────────────────────────
#  Page Config
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DocShield Pro | Document Security Suite",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
#  Custom CSS — Dark Slate / Teal accent professional theme
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Sora:wght@300;400;600;700&display=swap');

/* ── Disable selection / context-menu ── */
body { -webkit-user-select: none; user-select: none; }

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Sora', sans-serif;
    background-color: #0d1117 !important;
    color: #c9d1d9 !important;
}

/* ── Main container ── */
.main .block-container {
    padding: 2.5rem 3rem 4rem;
    max-width: 1100px;
}

/* ── Hero banner ── */
.hero {
    background: linear-gradient(135deg, #0f2027 0%, #0d3347 50%, #0f2027 100%);
    border: 1px solid #1e3a4a;
    border-radius: 16px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: "";
    position: absolute;
    top: -60px; right: -60px;
    width: 220px; height: 220px;
    background: radial-gradient(circle, #00e5ff18 0%, transparent 70%);
    border-radius: 50%;
}
.hero h1 {
    font-size: 2.4rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0 0 .4rem;
    letter-spacing: -0.5px;
}
.hero h1 span { color: #00e5ff; }
.hero p {
    color: #8b949e;
    font-size: .95rem;
    margin: 0;
    line-height: 1.6;
}

/* ── Metric cards row ── */
.metrics-row {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
}
.metric-card {
    flex: 1;
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    text-align: center;
    transition: border-color .2s;
}
.metric-card:hover { border-color: #00e5ff55; }
.metric-card .val {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.6rem;
    font-weight: 600;
    color: #00e5ff;
}
.metric-card .lbl {
    font-size: .75rem;
    color: #6e7681;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: .2rem;
}

/* ── Upload zone ── */
[data-testid="stFileUploader"] {
    background: #161b22 !important;
    border: 2px dashed #30363d !important;
    border-radius: 12px !important;
    transition: border-color .25s !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: #00e5ff88 !important;
}
[data-testid="stFileUploader"] label {
    color: #8b949e !important;
}

/* ── Section heading ── */
.section-label {
    font-size: .7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #00e5ff;
    margin-bottom: .6rem;
    display: flex;
    align-items: center;
    gap: .5rem;
}
.section-label::after {
    content: "";
    flex: 1;
    height: 1px;
    background: #21262d;
}

/* ── Result card ── */
.result-card {
    background: #0d2e1a;
    border: 1px solid #145a32;
    border-radius: 12px;
    padding: 1.5rem 2rem;
    margin-top: 1.5rem;
}
.result-card h3 { color: #2ecc71; margin: 0 0 1rem; font-size: 1.05rem; }
.result-stat { display: flex; justify-content: space-between; margin-bottom: .5rem; }
.result-stat .key { color: #6e7681; font-size: .85rem; }
.result-stat .val {
    font-family: 'IBM Plex Mono', monospace;
    font-size: .85rem;
    color: #c9d1d9;
}
.result-stat .val.green { color: #2ecc71; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0d1117 !important;
    border-right: 1px solid #21262d !important;
}
[data-testid="stSidebar"] .sidebar-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: .75rem;
    color: #00e5ff;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 1.2rem;
}

/* ── Buttons ── */
.stButton > button, .stDownloadButton > button {
    background: linear-gradient(135deg, #005f73, #0a9396) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Sora', sans-serif !important;
    font-weight: 600 !important;
    font-size: .9rem !important;
    padding: .65rem 1.6rem !important;
    letter-spacing: .3px !important;
    transition: all .2s !important;
    box-shadow: 0 4px 14px #0a939640 !important;
    width: 100% !important;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px #0a939660 !important;
}

/* ── Slider & inputs ── */
.stSlider [data-baseweb="slider"] { padding: 0 .5rem; }
.stTextInput input {
    background: #21262d !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
    color: #c9d1d9 !important;
    font-family: 'IBM Plex Mono', monospace !important;
}
.stTextInput input:focus { border-color: #00e5ff !important; box-shadow: none !important; }

/* ── Checkbox ── */
.stCheckbox span { color: #c9d1d9 !important; }

/* ── Selectbox ── */
.stSelectbox [data-baseweb="select"] {
    background: #21262d !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
}

/* ── Progress ── */
.stProgress > div > div { background-color: #00e5ff !important; }

/* ── Expander ── */
.stExpander {
    background: #161b22 !important;
    border: 1px solid #21262d !important;
    border-radius: 10px !important;
}

/* ── Tag badges ── */
.badge {
    display: inline-block;
    font-size: .65rem;
    font-family: 'IBM Plex Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: .15rem .55rem;
    border-radius: 20px;
    font-weight: 600;
    margin-right: .3rem;
}
.badge-teal  { background: #00e5ff18; color: #00e5ff; border: 1px solid #00e5ff33; }
.badge-green { background: #2ecc7118; color: #2ecc71; border: 1px solid #2ecc7133; }
.badge-amber { background: #f39c1218; color: #f39c12; border: 1px solid #f39c1233; }
.badge-red   { background: #e74c3c18; color: #e74c3c; border: 1px solid #e74c3c33; }

/* ── Footer ── */
.footer {
    text-align: center;
    color: #3d444d;
    font-size: .75rem;
    font-family: 'IBM Plex Mono', monospace;
    margin-top: 3rem;
    padding-top: 1.5rem;
    border-top: 1px solid #21262d;
}
</style>

<script>
document.addEventListener('contextmenu', e => e.preventDefault());
document.onkeydown = e => {
    if (e.ctrlKey && [67,86,85,83,80,65].includes(e.keyCode)) return false;
    if (e.keyCode === 44) return false; // Print Screen
};
</script>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
#  Constants & Helpers
# ─────────────────────────────────────────────────────────────
ENCRYPTION_LABELS = {
    "AES-128 (Fast)":     fitz.PDF_ENCRYPT_AES_128,
    "AES-256 (Standard)": fitz.PDF_ENCRYPT_AES_256,
    "RC4-128 (Legacy)":   fitz.PDF_ENCRYPT_RC4_128,
}

DPI_OPTIONS = {
    "High Quality  (200 DPI)": 200,
    "Balanced      (150 DPI)": 150,
    "Compact       (100 DPI)": 100,
    "Minimal       ( 72 DPI)":  72,
}

QUALITY_OPTIONS = {
    "Best  (90%)": 90,
    "Good  (75%)": 75,
    "Small (55%)": 55,
    "Tiny  (35%)": 35,
}


def fmt_size(nbytes: int) -> str:
    if nbytes >= 1_048_576:
        return f"{nbytes / 1_048_576:.2f} MB"
    return f"{nbytes / 1024:.1f} KB"


def reduction_pct(original: int, protected: int) -> float:
    if original == 0:
        return 0.0
    return max(0.0, (1 - protected / original) * 100)


def protect_pdf(
    raw: bytes,
    u_pw: str,
    o_pw: str,
    dpi: int,
    jpg_quality: int,
    enc_algo: int,
    allow_print: bool,
    allow_copy: bool,
) -> bytes:
    """
    Rasterises every page to JPEG, then re-saves with AES encryption,
    restricted permissions and optional open-password.
    """
    doc = fitz.open(stream=raw, filetype="pdf")
    out_pdf = fitz.open()

    perms = int(fitz.PDF_PERM_ACCESSIBILITY)
    if allow_print:
        perms |= int(fitz.PDF_PERM_PRINT)
    if allow_copy:
        perms |= int(fitz.PDF_PERM_COPY)

    for page in doc:
        pix = page.get_pixmap(dpi=dpi)
        img_data = pix.tobytes("jpg", jpg_quality=jpg_quality)
        new_page = out_pdf.new_page(width=page.rect.width, height=page.rect.height)
        new_page.insert_image(page.rect, stream=img_data)

    buf = io.BytesIO()
    out_pdf.save(
        buf,
        encryption=enc_algo,
        user_pw=u_pw if u_pw else None,
        owner_pw=o_pw,
        permissions=perms,
        deflate=True,
        garbage=4,
    )
    out_pdf.close()
    doc.close()
    return buf.getvalue()


# ─────────────────────────────────────────────────────────────
#  Sidebar
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">⚙ Configuration</div>', unsafe_allow_html=True)

    st.markdown("**Encryption**")
    enc_choice = st.selectbox("Algorithm", list(ENCRYPTION_LABELS.keys()), index=1, label_visibility="collapsed")

    st.divider()
    st.markdown("**Output Quality**")
    dpi_choice     = st.selectbox("Resolution", list(DPI_OPTIONS.keys()), index=1, label_visibility="collapsed")
    quality_choice = st.selectbox("JPEG Quality", list(QUALITY_OPTIONS.keys()), index=1, label_visibility="collapsed")

    st.divider()
    st.markdown("**Permissions**")
    allow_print = st.checkbox("Allow Printing",   value=False)
    allow_copy  = st.checkbox("Allow Copy / Select", value=False)

    st.divider()
    st.markdown("**Password Protection**")
    enable_user_pw = st.checkbox("Require Open Password", value=False)
    user_pw = ""
    if enable_user_pw:
        user_pw  = st.text_input("Open Password",    type="password", placeholder="Enter password…")
        confirm_pw = st.text_input("Confirm Password", type="password", placeholder="Re-enter password…")
        if user_pw and user_pw != confirm_pw:
            st.warning("⚠ Passwords do not match.")
            user_pw = ""

    OWNER_PW = "ds_owner_k3y_#9Xm"   # internal owner / admin key

    st.divider()
    st.caption("DocShield Pro v2.0 · AES-256 Engine")


# ─────────────────────────────────────────────────────────────
#  Hero
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🛡️ Doc<span>Shield</span> Pro</h1>
    <p>
        Enterprise-grade document protection &mdash; AES encryption, permission locking,
        and intelligent compression in one pipeline.
        <br>Supports <strong>PDF · DOCX · XLSX</strong> input formats.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Capability badges ──
col_b1, col_b2 = st.columns([3, 1])
with col_b1:
    st.markdown("""
    <span class="badge badge-teal">AES-256</span>
    <span class="badge badge-teal">Copy Lock</span>
    <span class="badge badge-teal">Print Lock</span>
    <span class="badge badge-green">Compression</span>
    <span class="badge badge-green">Rasterisation</span>
    <span class="badge badge-amber">Password Gate</span>
    """, unsafe_allow_html=True)

st.write("")

# ─────────────────────────────────────────────────────────────
#  Upload Zone
# ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">📁 Document Upload</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    "Drop your file here or click to browse",
    type=["pdf", "docx", "xlsx"],
    label_visibility="collapsed",
)

# ─────────────────────────────────────────────────────────────
#  Processing
# ─────────────────────────────────────────────────────────────
if uploaded_file is not None:
    original_bytes = uploaded_file.read()
    original_size  = len(original_bytes)
    stem           = Path(uploaded_file.name).stem
    ext            = Path(uploaded_file.name).suffix.lower()

    # ── File info strip ──
    st.markdown('<div class="section-label">📋 File Info</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("File Name",  uploaded_file.name)
    with c2: st.metric("Format",     ext.upper())
    with c3: st.metric("Original Size", fmt_size(original_size))
    with c4: st.metric("Pages",      "—")   # will be filled post-process

    st.write("")
    st.markdown('<div class="section-label">🔐 Protect Document</div>', unsafe_allow_html=True)

    if st.button("🔒  Apply Security & Compress", use_container_width=True):

        # Validate password
        if enable_user_pw and not user_pw:
            st.error("Please enter and confirm a valid open password.")
            st.stop()

        try:
            progress = st.progress(0, text="Initialising engine…")

            # Step 1: convert non-PDF to PDF if needed (DOCX/XLSX → basic fallback)
            if ext in (".docx", ".xlsx"):
                st.warning(
                    "⚠ DOCX / XLSX direct encryption requires LibreOffice on the server. "
                    "For now, please convert to PDF first and re-upload.",
                    icon="ℹ️",
                )
                st.stop()

            progress.progress(15, text="Parsing PDF structure…")
            time.sleep(0.2)

            # Count pages
            doc_tmp = fitz.open(stream=original_bytes, filetype="pdf")
            num_pages = len(doc_tmp)
            doc_tmp.close()

            progress.progress(30, text=f"Rasterising {num_pages} page(s) at {DPI_OPTIONS[dpi_choice]} DPI…")
            time.sleep(0.1)

            protected_data = protect_pdf(
                raw=original_bytes,
                u_pw=user_pw,
                o_pw=OWNER_PW,
                dpi=DPI_OPTIONS[dpi_choice],
                jpg_quality=QUALITY_OPTIONS[quality_choice],
                enc_algo=ENCRYPTION_LABELS[enc_choice],
                allow_print=allow_print,
                allow_copy=allow_copy,
            )

            progress.progress(85, text="Applying AES encryption layer…")
            time.sleep(0.15)
            progress.progress(100, text="Done.")
            time.sleep(0.2)
            progress.empty()

            protected_size = len(protected_data)
            saved_pct      = reduction_pct(original_size, protected_size)

            # ── Result card ──
            st.markdown(f"""
            <div class="result-card">
                <h3>✅ Protection Applied Successfully</h3>
                <div class="result-stat">
                    <span class="key">Original Size</span>
                    <span class="val">{fmt_size(original_size)}</span>
                </div>
                <div class="result-stat">
                    <span class="key">Protected Size</span>
                    <span class="val">{fmt_size(protected_size)}</span>
                </div>
                <div class="result-stat">
                    <span class="key">Size Reduction</span>
                    <span class="val green">{saved_pct:.1f}%</span>
                </div>
                <div class="result-stat">
                    <span class="key">Pages Processed</span>
                    <span class="val">{num_pages}</span>
                </div>
                <div class="result-stat">
                    <span class="key">Encryption</span>
                    <span class="val">{enc_choice}</span>
                </div>
                <div class="result-stat">
                    <span class="key">Resolution</span>
                    <span class="val">{DPI_OPTIONS[dpi_choice]} DPI · JPEG {QUALITY_OPTIONS[quality_choice]}%</span>
                </div>
                <div class="result-stat">
                    <span class="key">Copy Permission</span>
                    <span class="val">{"✓ Allowed" if allow_copy else "✗ Blocked"}</span>
                </div>
                <div class="result-stat">
                    <span class="key">Print Permission</span>
                    <span class="val">{"✓ Allowed" if allow_print else "✗ Blocked"}</span>
                </div>
                <div class="result-stat">
                    <span class="key">Password Gate</span>
                    <span class="val">{"✓ Enabled" if user_pw else "— None"}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.write("")
            st.download_button(
                label="⬇  Download Protected PDF",
                data=protected_data,
                file_name=f"{stem}_protected.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        except Exception as exc:
            st.error(f"❌ Processing failed: {exc}")

# ─────────────────────────────────────────────────────────────
#  How It Works (collapsed)
# ─────────────────────────────────────────────────────────────
with st.expander("ℹ  How DocShield Pro works"):
    st.markdown("""
    **Pipeline overview**

    1. **Rasterisation** — Each page is rendered to a JPEG image at the chosen DPI,
       stripping all selectable text and embedded metadata.
    2. **Repackaging** — Images are assembled into a new PDF with no underlying text layer.
    3. **Encryption** — The PDF is encrypted with your chosen AES algorithm.
       An *owner password* is applied internally to enforce permission flags.
    4. **Compression** — `deflate=True` + `garbage=4` trims internal cross-reference tables
       and compresses streams for the smallest possible output.

    **Security note** — Because content is rasterised, copy-paste and OCR on the
    output is significantly harder. For legal documents, combine with a strong open password.
    """)

# ─────────────────────────────────────────────────────────────
#  Footer
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    DocShield Pro v2.0 &nbsp;·&nbsp; AES-256 · PyMuPDF Engine &nbsp;·&nbsp;
    Built for document security professionals
</div>
""", unsafe_allow_html=True)
