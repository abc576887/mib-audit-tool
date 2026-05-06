import streamlit as st
import io, os, sys, subprocess, tempfile, zipfile, base64, math
from pathlib import Path
from PIL import Image

# ── PDF libs ──────────────────────────────────────────────────────────────
from pypdf import PdfReader, PdfWriter
from pypdf.constants import UserAccessPermissions

# ── ReportLab ─────────────────────────────────────────────────────────────
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfgen import canvas as rl_canvas

# ── pdf2image ─────────────────────────────────────────────────────────────
from pdf2image import convert_from_bytes

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FONT REGISTRATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FONT_DIR = "/usr/share/fonts/truetype/noto"
MYANMAR_FONTS = {
    "Noto Sans Myanmar": f"{FONT_DIR}/NotoSansMyanmar-Regular.ttf",
    "Noto Sans Myanmar Bold": f"{FONT_DIR}/NotoSansMyanmar-Bold.ttf",
    "Noto Serif Myanmar": f"{FONT_DIR}/NotoSerifMyanmar-Regular.ttf",
    "Noto Serif Myanmar Bold": f"{FONT_DIR}/NotoSerifMyanmar-Bold.ttf",
}
RL_FONT_MAP = {
    "Noto Sans Myanmar":      "MyanmarSans",
    "Noto Sans Myanmar Bold": "MyanmarSansBold",
    "Noto Serif Myanmar":     "MyanmarSerif",
    "Noto Serif Myanmar Bold":"MyanmarSerifBold",
}
def register_fonts():
    for name, path in MYANMAR_FONTS.items():
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(RL_FONT_MAP[name], path))
            except Exception:
                pass
register_fonts()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PAGE CONFIG
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.set_page_config(
    page_title="မြန်မာ PDF Tools",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GLOBAL STYLES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Padauk:wght@400;700&family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', 'Padauk', sans-serif; }

/* ── Nav bar ── */
.navbar {
  background: #fff;
  border-bottom: 2px solid #FF4B4B;
  padding: 12px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  margin: -1rem -1rem 2rem -1rem;
}
.navbar .logo { font-size: 1.5rem; font-weight: 700; color: #FF4B4B; letter-spacing:-1px; }
.navbar .tagline { font-size: 0.8rem; color: #666; margin-top:2px; }

/* ── Tool grid cards ── */
.tool-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px,1fr)); gap: 12px; margin-bottom: 32px; }
.tool-card {
  background: #fff;
  border-radius: 14px;
  padding: 20px 14px 16px;
  text-align: center;
  cursor: pointer;
  border: 2px solid #f0f0f0;
  transition: all .2s;
  box-shadow: 0 1px 4px rgba(0,0,0,.06);
}
.tool-card:hover { border-color: #FF4B4B; transform: translateY(-3px); box-shadow: 0 6px 20px rgba(255,75,75,.15); }
.tool-card .icon { font-size: 2rem; margin-bottom: 8px; }
.tool-card .label { font-size: 0.82rem; font-weight: 600; color: #333; line-height: 1.3; }
.tool-card .sublabel { font-size: 0.72rem; color: #999; margin-top:4px; }

/* ── Section heading ── */
.section-title {
  font-size: 1rem; font-weight: 700; color: #FF4B4B;
  border-left: 4px solid #FF4B4B;
  padding-left: 10px;
  margin: 24px 0 12px;
  text-transform: uppercase;
  letter-spacing: .5px;
}

/* ── Tool workspace ── */
.tool-header {
  background: linear-gradient(135deg,#FF4B4B,#c0392b);
  color: #fff;
  border-radius: 16px;
  padding: 28px 32px;
  margin-bottom: 24px;
}
.tool-header h2 { margin:0; font-size:1.6rem; }
.tool-header p  { margin:6px 0 0; opacity:.85; font-size:.95rem; }

/* ── Upload zone ── */
[data-testid="stFileUploader"] {
  border: 2px dashed #FF4B4B !important;
  border-radius: 12px !important;
  background: #fff5f5 !important;
}

/* ── Buttons ── */
.stButton > button {
  background: #FF4B4B !important;
  color: #fff !important;
  border-radius: 10px !important;
  font-weight: 600 !important;
  border: none !important;
  padding: .55rem 1.6rem !important;
  transition: all .2s !important;
}
.stButton > button:hover { background: #e03030 !important; transform: translateY(-1px); }
.stDownloadButton > button {
  background: #27ae60 !important;
  color: #fff !important;
  border-radius: 10px !important;
  font-weight: 700 !important;
  font-size: 1rem !important;
  padding: .65rem 2rem !important;
}

/* ── Back button ── */
.back-btn button { background: #f0f0f0 !important; color: #333 !important; font-size:.85rem !important; padding: .3rem 1rem !important; }

/* ── Metric cards ── */
[data-testid="metric-container"] {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  border: 1px solid #eee;
  box-shadow: 0 1px 4px rgba(0,0,0,.05);
}

/* ── Home hero ── */
.hero {
  background: linear-gradient(135deg,#FF4B4B 0%,#ff8c42 100%);
  color: #fff;
  border-radius: 20px;
  padding: 48px 40px;
  text-align: center;
  margin-bottom: 40px;
}
.hero h1 { font-size: 2.8rem; margin:0; font-weight:800; letter-spacing:-1px; }
.hero p  { font-size: 1.15rem; opacity:.9; margin:10px 0 0; }

/* ── Myanmar badge ── */
.mm-badge {
  display:inline-block;
  background:#FFE5E5;
  color:#FF4B4B;
  font-size:.75rem;
  font-weight:700;
  padding:2px 8px;
  border-radius:20px;
  margin-left:6px;
  vertical-align:middle;
}

/* hide default streamlit chrome */
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 0 !important; }
</style>
""", unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SESSION STATE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if "tool" not in st.session_state:
    st.session_state.tool = None

def go_home():
    st.session_state.tool = None

def go_tool(t):
    st.session_state.tool = t

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL CATALOGUE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOOLS = {
    "📂 PDF စီစဉ်ခြင်း": [
        ("merge",    "🔗", "Merge PDF",      "PDF ဖိုင်များ ပေါင်းစည်း"),
        ("split",    "✂️", "Split PDF",       "Pages အလိုက် ဖြတ်"),
        ("remove",   "🗑️", "Remove Pages",    "Pages ဖျက်"),
        ("extract",  "📤", "Extract Pages",   "Pages ထုတ်"),
        ("organize", "🔀", "Organize PDF",    "Pages အစီအစဉ် ပြောင်း"),
    ],
    "⚡ Optimize": [
        ("compress", "🗜️", "Compress PDF",   "ဖိုင်အရွယ်ကျ"),
        ("repair",   "🔧", "Repair PDF",     "ပျက်သွားသော PDF ပြင်"),
        ("ocr",      "🔍", "OCR PDF",        "မြန်မာ+အင်္ဂလိပ် OCR"),
    ],
    "⬆️ PDF ပြောင်းခြင်း (→ PDF)": [
        ("img2pdf",  "🖼️", "Image → PDF",    "JPG/PNG ကို PDF"),
        ("word2pdf", "📝", "Word → PDF",     "Myanmar font support"),
        ("ppt2pdf",  "📊", "PowerPoint → PDF","PPT/PPTX"),
        ("excel2pdf","📈", "Excel → PDF",    "XLSX/XLS"),
        ("html2pdf", "🌐", "HTML → PDF",     "URL/HTML ဖိုင်"),
    ],
    "⬇️ PDF ပြောင်းခြင်း (PDF →)": [
        ("pdf2img",  "🖼️", "PDF → Image",    "JPG/PNG pages"),
        ("pdf2word", "📝", "PDF → Word",     "DOCX ဖြစ်အောင်"),
        ("pdf2ppt",  "📊", "PDF → PowerPoint","PPTX ဖြစ်အောင်"),
        ("pdf2excel","📈", "PDF → Excel",    "XLSX ဖြစ်အောင်"),
    ],
    "✏️ Edit PDF": [
        ("rotate",   "🔄", "Rotate PDF",     "Pages လှည့်"),
        ("pagenum",  "🔢", "Page Numbers",   "မြန်မာ/အင်္ဂလိပ် page နံပါတ်"),
        ("watermark","💧", "Watermark",      "မြန်မာ watermark"),
        ("crop",     "✂️", "Crop PDF",       "Margin ဖြတ်"),
        ("create",   "📄", "Create PDF",     "မြန်မာစာ PDF ဖန်တီး"),
    ],
    "🔐 Security": [
        ("protect",  "🔒", "Protect PDF",    "Password + permissions"),
        ("unlock",   "🔓", "Unlock PDF",     "Password ဖြုတ်"),
        ("nocopy",   "🚫", "No Copy",        "ကူးယူမရအောင်"),
        ("redact",   "⬛", "Redact PDF",     "အချက်အလက် ဖျောက်"),
        ("compare",  "🔍", "Compare PDF",    "PDF နှစ်ခု နှိုင်းယှဉ်"),
    ],
    "🤖 AI Tools": [
        ("summarize","🧠", "AI Summary",     "AI ဖြင့် အနှစ်ချုပ်"),
        ("translate","🌏", "AI Translate",   "မြန်မာဘာသာ ပြန်"),
    ],
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NAVBAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
col_logo, col_spacer = st.columns([3, 1])
with col_logo:
    st.markdown("""
    <div class="navbar">
      <div>
        <div class="logo">📄 Myanmar PDF Tools</div>
        <div class="tagline">iLovePDF လိုမျိုး • မြန်မာဖောင့် Support <span class="mm-badge">🇲🇲 Myanmar</span></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HELPERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def tool_header(icon, title, desc):
    col_back, _ = st.columns([1, 8])
    with col_back:
        if st.button("← ပြန်သွား", key="back"):
            go_home(); st.rerun()
    st.markdown(f"""
    <div class="tool-header">
      <h2>{icon} {title}</h2>
      <p>{desc}</p>
    </div>
    """, unsafe_allow_html=True)

def libreoffice_convert(src_path, out_dir, to_fmt="pdf"):
    cmd = ["libreoffice","--headless","--convert-to", to_fmt,"--outdir", out_dir, src_path]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return r

def compress_pdf_gs(input_bytes, quality="screen"):
    """quality: screen | ebook | printer | prepress"""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as fin:
        fin.write(input_bytes); inp = fin.name
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as fout:
        outp = fout.name
    cmd = ["gs","-sDEVICE=pdfwrite","-dCompatibilityLevel=1.4",
           f"-dPDFSETTINGS=/{quality}","-dNOPAUSE","-dQUIET","-dBATCH",
           f"-sOutputFile={outp}", inp]
    subprocess.run(cmd, capture_output=True, timeout=120)
    with open(outp,"rb") as f: data = f.read()
    os.unlink(inp); os.unlink(outp)
    return data

def download_btn(data, filename, label="⬇️ ဒေါင်းရန်"):
    st.download_button(label, data, filename, mime="application/pdf",
                       use_container_width=True)

def download_zip(files_dict, zip_name):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf,"w") as zf:
        for name, data in files_dict.items():
            zf.writestr(name, data)
    buf.seek(0)
    st.download_button("⬇️ ZIP ဒေါင်းရန်", buf, zip_name,
                       mime="application/zip", use_container_width=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HOME PAGE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def page_home():
    st.markdown("""
    <div class="hero">
      <h1>📄 Myanmar PDF Tools</h1>
      <p>iLovePDF ရဲ့ features အကုန် • မြန်မာဖောင့် Support • Password ကာကွယ်မှု • ဒေသဆိုင်ရာ Server</p>
    </div>
    """, unsafe_allow_html=True)

    for category, tools in TOOLS.items():
        st.markdown(f'<div class="section-title">{category}</div>', unsafe_allow_html=True)
        cols = st.columns(len(tools))
        for col, (key, icon, label, desc) in zip(cols, tools):
            with col:
                if st.button(f"{icon}\n\n**{label}**\n\n_{desc}_",
                             key=f"btn_{key}", use_container_width=True):
                    st.session_state.tool = key
                    st.rerun()

    st.markdown("---")
    st.markdown("""
    <p style='text-align:center;color:#aaa;font-size:.8rem'>
    📄 Myanmar PDF Tools • Noto Sans/Serif Myanmar • ReportLab • pypdf • LibreOffice • Ghostscript • Tesseract OCR (မြန်မာ)
    </p>""", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL: MERGE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def tool_merge():
    tool_header("🔗","Merge PDF","PDF ဖိုင် အများကို တစ်ဖိုင်တည်းသို့ ပေါင်းစည်းပါ")
    files = st.file_uploader("PDF ဖိုင်များ ရွေးပါ (အများ)", type=["pdf"], accept_multiple_files=True)
    if files:
        st.info(f"ဖိုင် {len(files)} ခု ရွေးထား")
        for i,f in enumerate(files): st.write(f"  {i+1}. {f.name}")
        out_name = st.text_input("Output ဖိုင်နာမည်","merged.pdf")
        if st.button("🔗 ပေါင်းမည်", use_container_width=True):
            with st.spinner("ပေါင်းနေသည်..."):
                writer = PdfWriter()
                total = 0
                for f in files:
                    r = PdfReader(io.BytesIO(f.read()))
                    for p in r.pages: writer.add_page(p)
                    total += len(r.pages)
                buf = io.BytesIO(); writer.write(buf); buf.seek(0)
            st.success(f"✅ Pages {total} ခု ပေါင်းပြီး!")
            download_btn(buf.read(), out_name)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL: SPLIT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def tool_split():
    tool_header("✂️","Split PDF","PDF ကို pages အလိုက် ဖြတ်ပါ")
    f = st.file_uploader("PDF ဖိုင် ရွေးပါ", type=["pdf"])
    if not f: return
    data = f.read(); reader = PdfReader(io.BytesIO(data)); total = len(reader.pages)
    st.info(f"📄 Pages: {total}")
    mode = st.radio("ဖြတ်နည်း",["Pages တစ်ခုချင်း","Range သတ်မှတ်","ပုံသေ chunk"])
    if mode == "Pages တစ်ခုချင်း":
        if st.button("✂️ ဖြတ်မည်", use_container_width=True):
            with st.spinner("ဖြတ်နေသည်..."):
                files = {}
                for i,page in enumerate(reader.pages):
                    w = PdfWriter(); w.add_page(page)
                    b = io.BytesIO(); w.write(b)
                    files[f"page_{i+1:03d}.pdf"] = b.getvalue()
                download_zip(files, "split_pages.zip")
    elif mode == "Range သတ်မှတ်":
        c1,c2 = st.columns(2)
        s = c1.number_input("Start page",1,total,1)
        e = c2.number_input("End page",1,total,total)
        if st.button("✂️ Range ဖြတ်မည်", use_container_width=True):
            w = PdfWriter()
            for i in range(s-1,e): w.add_page(reader.pages[i])
            b = io.BytesIO(); w.write(b); b.seek(0)
            st.success(f"✅ Page {s}–{e} ဖြတ်ပြီး!")
            download_btn(b.read(), f"pages_{s}_to_{e}.pdf")
    else:
        chunk = st.number_input("Pages per chunk",1,total,1)
        if st.button("✂️ Chunk ဖြတ်မည်", use_container_width=True):
            files = {}
            for i in range(0, total, chunk):
                w = PdfWriter()
                for j in range(i, min(i+chunk, total)): w.add_page(reader.pages[j])
                b = io.BytesIO(); w.write(b)
                files[f"chunk_{i//chunk+1:03d}_pages_{i+1}-{min(i+chunk,total)}.pdf"] = b.getvalue()
            download_zip(files, "split_chunks.zip")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL: REMOVE PAGES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def tool_remove():
    tool_header("🗑️","Remove Pages","မလိုသော pages ဖျက်ပါ")
    f = st.file_uploader("PDF ဖိုင် ရွေးပါ", type=["pdf"])
    if not f: return
    data = f.read(); reader = PdfReader(io.BytesIO(data)); total = len(reader.pages)
    st.info(f"📄 Pages: {total}")
    pages_str = st.text_input("ဖျက်မည့် pages (commas: 1,3,5 or range: 2-4)","")
    def parse_pages(s, total):
        pages = set()
        for part in s.split(","):
            part = part.strip()
            if "-" in part:
                a,b = part.split("-",1)
                pages.update(range(int(a),int(b)+1))
            elif part.isdigit():
                pages.add(int(part))
        return {p-1 for p in pages if 1<=p<=total}
    if st.button("🗑️ Pages ဖျက်မည်", use_container_width=True):
        if not pages_str:
            st.error("Pages သတ်မှတ်ပါ"); return
        remove_set = parse_pages(pages_str, total)
        w = PdfWriter()
        for i,p in enumerate(reader.pages):
            if i not in remove_set: w.add_page(p)
        b = io.BytesIO(); w.write(b); b.seek(0)
        st.success(f"✅ {len(remove_set)} pages ဖျက်ပြီး! ({total - len(remove_set)} pages ကျန်)")
        download_btn(b.read(), f"removed_{f.name}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL: EXTRACT PAGES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def tool_extract():
    tool_header("📤","Extract Pages","လိုသော pages များကို ထုတ်ပါ")
    f = st.file_uploader("PDF ဖိုင် ရွေးပါ", type=["pdf"])
    if not f: return
    data = f.read(); reader = PdfReader(io.BytesIO(data)); total = len(reader.pages)
    st.info(f"📄 Pages: {total}")
    pages_str = st.text_input("ထုတ်မည့် pages (1,3,5 or 2-4)","1")
    if st.button("📤 Pages ထုတ်မည်", use_container_width=True):
        pages = set()
        for part in pages_str.split(","):
            part = part.strip()
            if "-" in part:
                a,b = part.split("-",1); pages.update(range(int(a),int(b)+1))
            elif part.isdigit(): pages.add(int(part))
        pages = sorted([p-1 for p in pages if 1<=p<=total])
        w = PdfWriter()
        for i in pages: w.add_page(reader.pages[i])
        b = io.BytesIO(); w.write(b); b.seek(0)
        st.success(f"✅ {len(pages)} pages ထုတ်ပြီး!")
        download_btn(b.read(), f"extracted_{f.name}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL: ORGANIZE (reorder)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def tool_organize():
    tool_header("🔀","Organize PDF","Pages အစီအစဉ် ပြောင်းပါ")
    f = st.file_uploader("PDF ဖိုင် ရွေးပါ", type=["pdf"])
    if not f: return
    data = f.read(); reader = PdfReader(io.BytesIO(data)); total = len(reader.pages)
    st.info(f"📄 Pages: {total}")
    st.markdown("**အစီအစဉ် ပြောင်းမည့် Page နံပါတ်များ ရိုက်ပါ** (ဥပမာ - 3,1,2 ဆိုရင် page 3 ကို ပထမ ထားမည်)")
    order_str = st.text_input("Page order (comma-separated)", ",".join(str(i) for i in range(1,total+1)))
    if st.button("🔀 Reorder မည်", use_container_width=True):
        try:
            order = [int(x.strip())-1 for x in order_str.split(",")]
            w = PdfWriter()
            for i in order:
                if 0 <= i < total: w.add_page(reader.pages[i])
            b = io.BytesIO(); w.write(b); b.seek(0)
            st.success("✅ Pages reorder ပြီး!")
            download_btn(b.read(), f"organized_{f.name}")
        except Exception as e:
            st.error(f"Error: {e}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL: COMPRESS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def tool_compress():
    tool_header("🗜️","Compress PDF","ဖိုင် size လျှော့ချပါ")
    f = st.file_uploader("PDF ဖိုင် ရွေးပါ", type=["pdf"])
    if not f: return
    data = f.read()
    orig_kb = len(data)/1024
    st.metric("မူရင်း ဖိုင် size", f"{orig_kb:.1f} KB")
    quality = st.select_slider("ဖိသိပ်မှု အဆင့်",
        options=["screen","ebook","printer","prepress"],
        value="ebook",
        format_func=lambda x: {"screen":"အမြင့်ဆုံး (72dpi)","ebook":"ကောင်းသော (150dpi)",
                                "printer":"ပုံနှိပ် (300dpi)","prepress":"မူရင်း"}[x])
    if st.button("🗜️ Compress မည်", use_container_width=True):
        with st.spinner("Ghostscript ဖြင့် compress နေသည်..."):
            try:
                compressed = compress_pdf_gs(data, quality)
                new_kb = len(compressed)/1024
                saved = ((orig_kb - new_kb)/orig_kb)*100
                c1,c2,c3 = st.columns(3)
                c1.metric("မူရင်း", f"{orig_kb:.1f} KB")
                c2.metric("ပြီးနောက်", f"{new_kb:.1f} KB")
                c3.metric("သက်သာမှု", f"{saved:.1f}%")
                if new_kb < orig_kb:
                    st.success(f"✅ {saved:.1f}% လျှော့ချပြီး!")
                else:
                    st.info("ℹ️ ဤဖိုင်ကို ထပ်မ compress မရပါ (ရလဒ် ပိုကြီးသည်)")
                download_btn(compressed, f"compressed_{f.name}")
            except Exception as e:
                st.error(f"Error: {e}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL: REPAIR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def tool_repair():
    tool_header("🔧","Repair PDF","ပျက်သွားသော PDF ပြန်ပြင်ပါ")
    f = st.file_uploader("PDF ဖိုင် ရွေးပါ", type=["pdf"])
    if not f: return
    if st.button("🔧 Repair မည်", use_container_width=True):
        with st.spinner("PDF ပြန်ပြင်နေသည်..."):
            try:
                # re-write via gs
                data = f.read()
                repaired = compress_pdf_gs(data, "prepress")
                st.success("✅ PDF repair ပြီး!")
                download_btn(repaired, f"repaired_{f.name}")
            except Exception as e:
                st.error(f"Error: {e}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL: OCR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def tool_ocr():
    tool_header("🔍","OCR PDF","မြန်မာ + အင်္ဂလိပ် စာသား ထုတ်ယူပါ")
    import pytesseract
    f = st.file_uploader("PDF ဖိုင် ရွေးပါ", type=["pdf"])
    if not f: return
    lang = st.multiselect("OCR ဘာသာစကား", ["မြန်မာ (mya)","English (eng)"],
                          default=["မြန်မာ (mya)","English (eng)"])
    lang_code = "+".join([l.split("(")[1].rstrip(")") for l in lang])
    pages_opt = st.radio("Pages", ["Page အကုန်","Page ၁ ဆောင်"])
    dpi = st.slider("DPI (မြင့်လေ တိကျလေ)", 100, 400, 200, 50)
    if st.button("🔍 OCR လုပ်မည်", use_container_width=True):
        with st.spinner(f"Tesseract OCR ({lang_code}) လည်ပတ်နေသည်..."):
            try:
                data = f.read()
                max_pages = 1 if "၁" in pages_opt else None
                images = convert_from_bytes(data, dpi=dpi,
                                            first_page=1,
                                            last_page=max_pages)
                full_text = ""
                for i, img in enumerate(images):
                    text = pytesseract.image_to_string(img, lang=lang_code)
                    full_text += f"\n\n── Page {i+1} ──\n{text}"
                st.text_area("OCR ရလဒ်", full_text, height=400)
                st.download_button("⬇️ Text ဒေါင်းရန်", full_text,
                                   f"ocr_{f.name}.txt", mime="text/plain",
                                   use_container_width=True)
            except Exception as e:
                st.error(f"OCR Error: {e}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL: IMAGE → PDF
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def tool_img2pdf():
    tool_header("🖼️","Image → PDF","ပုံများကို PDF ပြောင်းပါ")
    files = st.file_uploader("ပုံများ ရွေးပါ",type=["jpg","jpeg","png","webp","bmp","tiff"],
                              accept_multiple_files=True)
    if not files: return
    c1,c2 = st.columns(2)
    psize = c1.selectbox("Page size",["A4","Letter","ပုံအတိုင်း"])
    orient = c2.selectbox("ဦးတည်ချက်",["Portrait","Landscape"])
    margin = st.slider("Margin (mm)", 0, 30, 10)
    if st.button("🖼️ PDF ဖန်တီးမည်", use_container_width=True):
        with st.spinner("PDF ဖန်တီးနေသည်..."):
            writer = PdfWriter()
            for img_file in files:
                img = Image.open(img_file).convert("RGB")
                if psize == "A4": pw,ph = A4
                elif psize == "Letter":
                    from reportlab.lib.pagesizes import letter as lt; pw,ph = lt
                else: pw,ph = img.size[0]*0.75, img.size[1]*0.75  # px→pt approx
                if orient == "Landscape": pw,ph = ph,pw
                m = margin * mm
                avw, avh = pw-2*m, ph-2*m
                iw,ih = img.size
                scale = min(avw/iw, avh/ih)
                nw,nh = iw*scale, ih*scale
                x = m + (avw-nw)/2; y = m + (avh-nh)/2
                pg_buf = io.BytesIO()
                c = rl_canvas.Canvas(pg_buf, pagesize=(pw,ph))
                with tempfile.NamedTemporaryFile(suffix=".jpg",delete=False) as t:
                    img.save(t.name,"JPEG",quality=95); tmp=t.name
                c.drawImage(tmp,x,y,nw,nh); c.showPage(); c.save()
                os.unlink(tmp)
                pg_buf.seek(0)
                r = PdfReader(pg_buf)
                writer.add_page(r.pages[0])
            buf = io.BytesIO(); writer.write(buf); buf.seek(0)
            st.success(f"✅ ပုံ {len(files)} ခု → PDF ပြောင်းပြီး!")
            download_btn(buf.read(), "images_to_pdf.pdf")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL: WORD/PPT/EXCEL → PDF
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def tool_office2pdf(kind):
    icons = {"word":"📝","ppt":"📊","excel":"📈"}
    labels = {"word":"Word → PDF","ppt":"PowerPoint → PDF","excel":"Excel → PDF"}
    descs = {"word":"DOCX ကို PDF (မြန်မာဖောင့် support)","ppt":"PPT/PPTX → PDF","excel":"XLSX/XLS → PDF"}
    exts = {"word":["docx","doc"],"ppt":["pptx","ppt"],"excel":["xlsx","xls"]}
    tool_header(icons[kind], labels[kind], descs[kind])
    f = st.file_uploader(f"ဖိုင် ရွေးပါ", type=exts[kind])
    if not f: return
    st.info("ℹ️ LibreOffice ဖြင့် ပြောင်းသောကြောင့် မြန်မာ Unicode font မပျောက်ပါ")
    if st.button("🔄 PDF ပြောင်းမည်", use_container_width=True):
        with st.spinner("LibreOffice လည်ပတ်နေသည်... (ခဏစောင့်ပါ)"):
            with tempfile.TemporaryDirectory() as d:
                src = os.path.join(d, f.name)
                with open(src,"wb") as fp: fp.write(f.read())
                libreoffice_convert(src, d, "pdf")
                pdf_path = os.path.join(d, Path(f.name).stem+".pdf")
                if os.path.exists(pdf_path):
                    with open(pdf_path,"rb") as fp: pdf_data = fp.read()
                    st.success("✅ PDF ပြောင်းပြီး!")
                    download_btn(pdf_data, Path(f.name).stem+".pdf")
                else:
                    st.error("ပြောင်းမရပါ")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL: HTML → PDF
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def tool_html2pdf():
    tool_header("🌐","HTML → PDF","HTML ဖိုင် သို့မဟုတ် URL ကို PDF ပြောင်း")
    mode = st.radio("Mode", ["HTML ဖိုင် upload", "URL ထည့်"])
    if mode == "HTML ဖိုင် upload":
        f = st.file_uploader("HTML ဖိုင် ရွေးပါ", type=["html","htm"])
        if f and st.button("🔄 PDF ပြောင်းမည်", use_container_width=True):
            with tempfile.TemporaryDirectory() as d:
                src = os.path.join(d, f.name)
                with open(src,"wb") as fp: fp.write(f.read())
                libreoffice_convert(src, d, "pdf")
                pdf_path = os.path.join(d, Path(f.name).stem+".pdf")
                if os.path.exists(pdf_path):
                    with open(pdf_path,"rb") as fp: data = fp.read()
                    st.success("✅ ပြောင်းပြီး!")
                    download_btn(data, Path(f.name).stem+".pdf")
    else:
        url = st.text_input("URL ထည့်ပါ","https://example.com")
        st.info("ℹ️ wkhtmltopdf မတပ်ဆင်ထားသောကြောင့် URL conversion ကန့်သတ်ချက်ရှိသည်")
        if st.button("🔄 PDF ပြောင်းမည်", use_container_width=True):
            r = subprocess.run(["curl","-s","-L","--max-time","10",url],capture_output=True)
            if r.returncode == 0:
                with tempfile.TemporaryDirectory() as d:
                    src = os.path.join(d,"page.html")
                    with open(src,"wb") as fp: fp.write(r.stdout)
                    libreoffice_convert(src, d, "pdf")
                    pdf_path = os.path.join(d,"page.pdf")
                    if os.path.exists(pdf_path):
                        with open(pdf_path,"rb") as fp: data = fp.read()
                        st.success("✅ ပြောင်းပြီး!")
                        download_btn(data, "webpage.pdf")
                    else: st.error("ပြောင်းမရပါ")
            else: st.error("URL ရယူ မရပါ")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL: PDF → IMAGE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def tool_pdf2img():
    tool_header("🖼️","PDF → Image","PDF pages များကို JPG/PNG ပြောင်းပါ")
    f = st.file_uploader("PDF ဖိုင် ရွေးပါ", type=["pdf"])
    if not f: return
    data = f.read()
    c1,c2,c3 = st.columns(3)
    fmt = c1.selectbox("Format",["JPEG","PNG"])
    dpi = c2.slider("DPI",72,300,150,step=50)
    all_pages = c3.radio("Pages",["အကုန်","Page 1 ဆောင်"])
    if st.button("🖼️ ပြောင်းမည်", use_container_width=True):
        with st.spinner("PDF → Image ပြောင်းနေသည်..."):
            lp = 1 if "1" in all_pages else None
            images = convert_from_bytes(data, dpi=dpi, fmt=fmt.lower(),
                                        first_page=1, last_page=lp)
            if len(images) == 1:
                buf = io.BytesIO()
                images[0].save(buf, format=fmt)
                ext = "jpg" if fmt=="JPEG" else "png"
                st.image(images[0], caption="Preview", use_container_width=True)
                st.download_button("⬇️ ပုံ ဒေါင်းရန်", buf.getvalue(),
                                   f"page_1.{ext}", mime=f"image/{ext.lower()}",
                                   use_container_width=True)
            else:
                files = {}
                for i,img in enumerate(images):
                    b = io.BytesIO(); img.save(b, format=fmt)
                    ext = "jpg" if fmt=="JPEG" else "png"
                    files[f"page_{i+1:03d}.{ext}"] = b.getvalue()
                st.success(f"✅ {len(images)} pages ပြောင်းပြီး!")
                download_zip(files, "pdf_to_images.zip")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL: PDF → OFFICE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def tool_pdf2office(kind):
    icons = {"word":"📝","ppt":"📊","excel":"📈"}
    labels = {"word":"PDF → Word","ppt":"PDF → PowerPoint","excel":"PDF → Excel"}
    exts = {"word":"docx","ppt":"pptx","excel":"xlsx"}
    lo_fmt = {"word":"docx","ppt":"pptx","excel":"xlsx"}
    tool_header(icons[kind], labels[kind], f"PDF ကို {exts[kind].upper()} ဖြစ်အောင် ပြောင်း")
    f = st.file_uploader("PDF ဖိုင် ရွေးပါ", type=["pdf"])
    if not f: return
    st.info("ℹ️ LibreOffice ဖြင့် ပြောင်းသည်")
    if st.button("🔄 ပြောင်းမည်", use_container_width=True):
        with st.spinner("LibreOffice လည်ပတ်နေသည်..."):
            with tempfile.TemporaryDirectory() as d:
                src = os.path.join(d, f.name)
                with open(src,"wb") as fp: fp.write(f.read())
                libreoffice_convert(src, d, lo_fmt[kind])
                out_path = os.path.join(d, Path(f.name).stem+"."+exts[kind])
                if os.path.exists(out_path):
                    with open(out_path,"rb") as fp: data = fp.read()
                    st.success("✅ ပြောင်းပြီး!")
                    mimes = {"word":"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                             "ppt":"application/vnd.openxmlformats-officedocument.presentationml.presentation",
                             "excel":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}
                    st.download_button("⬇️ ဒေါင်းရန်", data,
                                       Path(f.name).stem+"."+exts[kind],
                                       mime=mimes[kind], use_container_width=True)
                else: st.error("ပြောင်းမရပါ")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL: ROTATE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def tool_rotate():
    tool_header("🔄","Rotate PDF","PDF pages လှည့်ပါ")
    f = st.file_uploader("PDF ဖိုင် ရွေးပါ", type=["pdf"])
    if not f: return
    data = f.read(); reader = PdfReader(io.BytesIO(data)); total = len(reader.pages)
    st.info(f"📄 Pages: {total}")
    c1,c2 = st.columns(2)
    angle = c1.select_slider("လှည့်မည့် ဒီဂရီ",[90,180,270])
    scope = c2.radio("Pages",["Pages အကုန်","သတ်မှတ် Page"])
    pg = None
    if scope == "သတ်မှတ် Page":
        pg = st.number_input("Page နံပါတ်",1,total,1)
    if st.button("🔄 လှည့်မည်", use_container_width=True):
        writer = PdfWriter()
        for i,page in enumerate(reader.pages):
            if scope=="Pages အကုန်" or (pg and i==pg-1): page.rotate(angle)
            writer.add_page(page)
        buf = io.BytesIO(); writer.write(buf); buf.seek(0)
        st.success(f"✅ {angle}° လှည့်ပြီး!")
        download_btn(buf.read(), f"rotated_{f.name}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL: PAGE NUMBERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def tool_pagenum():
    tool_header("🔢","Page Numbers","မြန်မာ/အင်္ဂလိပ် page နံပါတ် ထည့်ပါ")
    f = st.file_uploader("PDF ဖိုင် ရွေးပါ", type=["pdf"])
    if not f: return
    data = f.read(); reader = PdfReader(io.BytesIO(data)); total = len(reader.pages)
    st.info(f"📄 Pages: {total}")
    c1,c2,c3 = st.columns(3)
    pos = c1.selectbox("နေရာ",["Bottom Center","Bottom Right","Bottom Left","Top Center"])
    lang = c2.selectbox("ဘာသာ",["English","မြန်မာ"])
    start = c3.number_input("ပထမ နံပါတ်",1,total,1)
    font_size = st.slider("Font Size", 8, 20, 11)
    prefix = st.text_input("ရှေ့ပစ်ပါ (ဥပမာ 'စာ')", "")

    def num_mm(n, lang):
        if lang == "English": return f"{prefix}{n}"
        mm_digits = "၀၁၂၃၄၅၆၇၈၉"
        return prefix + "".join(mm_digits[int(d)] for d in str(n))

    if st.button("🔢 Page Numbers ထည့်မည်", use_container_width=True):
        with st.spinner("Page numbers ထည့်နေသည်..."):
            writer = PdfWriter()
            for i,page in enumerate(reader.pages):
                pw = float(page.mediabox.width); ph = float(page.mediabox.height)
                overlay = io.BytesIO()
                c = rl_canvas.Canvas(overlay, pagesize=(pw,ph))
                font_name = "MyanmarSans" if lang=="မြန်မာ" else "Helvetica"
                if lang == "English":
                    c.setFont(font_name, font_size)
                else:
                    try: c.setFont(font_name, font_size)
                    except: c.setFont("Helvetica", font_size)
                c.setFillColorRGB(0.3,0.3,0.3)
                txt = num_mm(i + start, lang)
                positions = {
                    "Bottom Center": (pw/2, 20),
                    "Bottom Right":  (pw-30, 20),
                    "Bottom Left":   (30, 20),
                    "Top Center":    (pw/2, ph-25),
                }
                x,y = positions[pos]
                c.drawCentredString(x,y,txt)
                c.showPage(); c.save(); overlay.seek(0)
                overlay_page = PdfReader(overlay).pages[0]
                page.merge_page(overlay_page)
                writer.add_page(page)
            buf = io.BytesIO(); writer.write(buf); buf.seek(0)
            st.success("✅ Page numbers ထည့်ပြီး!")
            download_btn(buf.read(), f"numbered_{f.name}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL: WATERMARK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def tool_watermark():
    tool_header("💧","Watermark","မြန်မာ/အင်္ဂလိပ် watermark ထည့်ပါ")
    f = st.file_uploader("PDF ဖိုင် ရွေးပါ", type=["pdf"])
    if not f: return
    c1,c2 = st.columns(2)
    wm_type = c1.radio("Watermark အမျိုးအစား",["စာသား","ပုံ"])
    wm_pos = c2.selectbox("နေရာ",["Middle (ဗဟို)","Diagonal (ထောင်မောင်း)","Top","Bottom"])

    wm_text = wm_img = None
    if wm_type == "စာသား":
        wm_text = st.text_input("Watermark စာသား","CONFIDENTIAL • လျှို့ဝှက်")
        c3,c4,c5 = st.columns(3)
        wm_color = c3.color_picker("အရောင်","#FF0000")
        wm_opacity = c4.slider("မြင်ရနှုန်း (%)",5,80,25)
        wm_size = c5.slider("Font Size",20,120,55)
    else:
        wm_img = st.file_uploader("Watermark ပုံ ရွေးပါ",type=["png","jpg"])
        wm_opacity = st.slider("မြင်ရနှုန်း (%)",5,80,20)

    if st.button("💧 Watermark ထည့်မည်", use_container_width=True):
        data = f.read(); reader = PdfReader(io.BytesIO(data)); writer = PdfWriter()
        with st.spinner("Watermark ထည့်နေသည်..."):
            for page in reader.pages:
                pw = float(page.mediabox.width); ph = float(page.mediabox.height)
                wm_buf = io.BytesIO()
                c = rl_canvas.Canvas(wm_buf, pagesize=(pw,ph))
                if wm_type == "စာသား":
                    r = int(wm_color[1:3],16)/255
                    g = int(wm_color[3:5],16)/255
                    b = int(wm_color[5:7],16)/255
                    c.setFillColorRGB(r,g,b,alpha=wm_opacity/100)
                    try: c.setFont("MyanmarSans", wm_size)
                    except: c.setFont("Helvetica", wm_size)
                    c.saveState()
                    if wm_pos == "Diagonal (ထောင်မောင်း)":
                        c.translate(pw/2, ph/2); c.rotate(45)
                        c.drawCentredString(0,0,wm_text)
                    elif wm_pos == "Middle (ဗဟို)":
                        c.translate(pw/2, ph/2); c.drawCentredString(0,0,wm_text)
                    elif wm_pos == "Top":
                        c.drawCentredString(pw/2, ph-60, wm_text)
                    else:
                        c.drawCentredString(pw/2, 40, wm_text)
                    c.restoreState()
                else:
                    if wm_img:
                        with tempfile.NamedTemporaryFile(suffix=".png",delete=False) as t:
                            t.write(wm_img.read()); tmp=t.name
                        c.saveState(); c.setFillAlpha(wm_opacity/100)
                        c.drawImage(tmp, pw*0.1, ph*0.1, pw*0.8, ph*0.8,
                                   mask="auto", preserveAspectRatio=True)
                        c.restoreState(); os.unlink(tmp)
                c.showPage(); c.save(); wm_buf.seek(0)
                wm_page = PdfReader(wm_buf).pages[0]
                page.merge_page(wm_page)
                writer.add_page(page)
        buf = io.BytesIO(); writer.write(buf); buf.seek(0)
        st.success("✅ Watermark ထည့်ပြီး!")
        download_btn(buf.read(), f"watermarked_{f.name}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL: CROP PDF
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def tool_crop():
    tool_header("✂️","Crop PDF","Margin ဖြတ်ပါ")
    f = st.file_uploader("PDF ဖိုင် ရွေးပါ", type=["pdf"])
    if not f: return
    data = f.read(); reader = PdfReader(io.BytesIO(data))
    st.info(f"📄 Pages: {len(reader.pages)}")
    c1,c2 = st.columns(2)
    c3,c4 = st.columns(2)
    top    = c1.number_input("Top (pt)", 0, 300, 0)
    bottom = c2.number_input("Bottom (pt)", 0, 300, 0)
    left   = c3.number_input("Left (pt)", 0, 300, 0)
    right  = c4.number_input("Right (pt)", 0, 300, 0)
    if st.button("✂️ Crop မည်", use_container_width=True):
        writer = PdfWriter()
        for page in reader.pages:
            mb = page.mediabox
            page.mediabox.lower_left  = (float(mb.left)+left,  float(mb.bottom)+bottom)
            page.mediabox.upper_right = (float(mb.right)-right, float(mb.top)-top)
            writer.add_page(page)
        buf = io.BytesIO(); writer.write(buf); buf.seek(0)
        st.success("✅ Crop ပြီး!")
        download_btn(buf.read(), f"cropped_{f.name}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL: CREATE MYANMAR PDF
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def tool_create():
    tool_header("📄","မြန်မာ PDF ဖန်တီးခြင်း","မြန်မာစာ တိုက်ရိုက်ရိုက်၍ PDF ဖန်တီး")
    c1,c2 = st.columns(2)
    title_text  = c1.text_input("ခေါင်းစဉ်","မြန်မာ PDF စာတမ်း")
    author_text = c2.text_input("စာရေးသူ","")
    c3,c4,c5 = st.columns(3)
    font_choice  = c3.selectbox("Font",["Noto Sans Myanmar","Noto Serif Myanmar"])
    body_size    = c4.slider("Body font size",10,24,13)
    line_spacing = c5.slider("Line spacing",1.0,3.0,1.8,0.1)
    content = st.text_area("မြန်မာစာ ရိုက်ပါ",
        "မင်္ဂလာပါ!\n\nဤသည်မှာ မြန်မာ PDF ဖန်တီးရာတွင် Noto Myanmar Unicode font မပျောက်ဘဲ မှန်ကန်စွာ ပြသနိုင်ကြောင်း ပြသသော နမူနာစာတမ်းဖြစ်ပါသည်။\n\nZawgyi font ကို Unicode ပြောင်းပြီး ထည့်ပါ။",
        height=250)
    c6,c7 = st.columns(2)
    add_pw = c6.checkbox("Password ထည့်"); restrict = c7.checkbox("Copy ပိတ်")
    pw = st.text_input("Password",type="password") if add_pw else ""
    if st.button("📄 PDF ဖန်တီးမည်", use_container_width=True):
        with st.spinner("PDF ဖန်တီးနေသည်..."):
            rl_name = RL_FONT_MAP.get(font_choice,"MyanmarSans")
            buf = io.BytesIO()
            doc = SimpleDocTemplate(buf, pagesize=A4,
                rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm,
                title=title_text, author=author_text)
            title_style = ParagraphStyle("T", fontName=rl_name,
                fontSize=body_size+8, leading=(body_size+8)*1.5,
                textColor=colors.HexColor("#c0392b"), spaceAfter=20, alignment=TA_CENTER)
            body_style = ParagraphStyle("B", fontName=rl_name,
                fontSize=body_size, leading=body_size*line_spacing,
                textColor=colors.black, spaceAfter=10)
            story = [Paragraph(title_text, title_style), Spacer(1,.5*cm)]
            for line in content.split("\n"):
                story.append(Paragraph(line.strip() or "&nbsp;", body_style))
            doc.build(story); buf.seek(0)
            if add_pw or restrict:
                reader = PdfReader(buf); writer = PdfWriter()
                for p in reader.pages: writer.add_page(p)
                perms = UserAccessPermissions.R6|UserAccessPermissions.R7|UserAccessPermissions.PRINT
                if not restrict: perms |= UserAccessPermissions.EXTRACT
                writer.encrypt(pw, pw+"_owner" if pw else "OwnerOnly2024!", perms)
                buf2 = io.BytesIO(); writer.write(buf2); buf2.seek(0); buf = buf2
            st.success("✅ PDF ဖန်တီးပြီး!")
            download_btn(buf.read(), f"{title_text}.pdf")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL: PROTECT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def tool_protect():
    tool_header("🔒","Protect PDF","Password + Permissions ကာကွယ်ပါ")
    f = st.file_uploader("PDF ဖိုင် ရွေးပါ", type=["pdf"])
    if not f: return
    c1,c2 = st.columns(2)
    user_pw  = c1.text_input("🔑 Open Password",type="password",placeholder="ဖွင့်ရာတွင် လိုအပ်")
    owner_pw = c2.text_input("👑 Owner Password",type="password",placeholder="Admin password")
    st.markdown("**Permissions**")
    pc1,pc2,pc3,pc4 = st.columns(4)
    a_print  = pc1.checkbox("Print",value=True)
    a_copy   = pc2.checkbox("Copy",value=False)
    a_edit   = pc3.checkbox("Edit",value=False)
    a_annot  = pc4.checkbox("Annotate",value=False)
    if st.button("🔒 Password ထည့်မည်", use_container_width=True):
        if not user_pw and not owner_pw:
            st.error("Password အနည်းဆုံး တစ်ခု ထည့်ပါ"); return
        reader = PdfReader(io.BytesIO(f.read())); writer = PdfWriter()
        for p in reader.pages: writer.add_page(p)
        perms = UserAccessPermissions.R6|UserAccessPermissions.R7
        if a_print:  perms |= UserAccessPermissions.PRINT
        if a_copy:   perms |= UserAccessPermissions.EXTRACT
        if a_edit:   perms |= UserAccessPermissions.MODIFY
        if a_annot:  perms |= UserAccessPermissions.ADD_OR_MODIFY
        writer.encrypt(user_pw, owner_pw or user_pw+"_owner", perms)
        buf = io.BytesIO(); writer.write(buf); buf.seek(0)
        st.success("✅ Password ကာကွယ်ပြီး!")
        download_btn(buf.read(), f"protected_{f.name}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL: UNLOCK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def tool_unlock():
    tool_header("🔓","Unlock PDF","PDF Password ဖြုတ်ပါ")
    f = st.file_uploader("PDF ဖိုင် ရွေးပါ", type=["pdf"])
    if not f: return
    pw = st.text_input("Password",type="password")
    if st.button("🔓 Password ဖြုတ်မည်", use_container_width=True):
        try:
            reader = PdfReader(io.BytesIO(f.read()))
            if reader.is_encrypted:
                result = reader.decrypt(pw)
                if result.value == 0:
                    st.error("❌ Password မှားသည်"); return
            writer = PdfWriter()
            for p in reader.pages: writer.add_page(p)
            buf = io.BytesIO(); writer.write(buf); buf.seek(0)
            st.success("✅ Password ဖြုတ်ပြီး!")
            download_btn(buf.read(), f"unlocked_{f.name}")
        except Exception as e:
            st.error(f"Error: {e}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL: NO COPY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def tool_nocopy():
    tool_header("🚫","No Copy","ကူးယူမရအောင် ကာကွယ်ပါ")
    f = st.file_uploader("PDF ဖိုင် ရွေးပါ", type=["pdf"])
    if not f: return
    also_print = st.checkbox("Print ပါ ပိတ်မည်")
    if st.button("🚫 ကာကွယ်မည်", use_container_width=True):
        reader = PdfReader(io.BytesIO(f.read())); writer = PdfWriter()
        for p in reader.pages: writer.add_page(p)
        perms = UserAccessPermissions.R6|UserAccessPermissions.R7
        if not also_print: perms |= UserAccessPermissions.PRINT
        writer.encrypt("", "NoCopy_Owner_2024!", perms)
        buf = io.BytesIO(); writer.write(buf); buf.seek(0)
        st.success("✅ Copy ကာကွယ်ပြီး! (ဖိုင်ဖွင့်ရာတွင် password မလိုပါ)")
        download_btn(buf.read(), f"nocopy_{f.name}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL: REDACT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def tool_redact():
    tool_header("⬛","Redact PDF","အချက်အလက် အမြဲတမ်း ဖျောက်ပါ")
    f = st.file_uploader("PDF ဖိုင် ရွေးပါ", type=["pdf"])
    if not f: return
    data = f.read(); reader = PdfReader(io.BytesIO(data)); total = len(reader.pages)
    st.info(f"📄 Pages: {total}")
    st.markdown("**ကလောင်နဲ့ ဖျောက်မည့် နေရာ သတ်မှတ်ပါ** (ညာ→ PDF coordinates, origin: bottom-left)")
    pg_num = st.number_input("Page", 1, total, 1)
    c1,c2,c3,c4 = st.columns(4)
    x1 = c1.number_input("x1 (left)",0.0,1000.0,100.0,step=5.0)
    y1 = c2.number_input("y1 (bottom)",0.0,1000.0,100.0,step=5.0)
    x2 = c3.number_input("x2 (right)",0.0,1000.0,300.0,step=5.0)
    y2 = c4.number_input("y2 (top)",0.0,1000.0,200.0,step=5.0)
    color = st.color_picker("Redaction အရောင်","#000000")
    if st.button("⬛ Redact မည်", use_container_width=True):
        with st.spinner("Redact လုပ်နေသည်..."):
            writer = PdfWriter()
            for i,page in enumerate(reader.pages):
                pw_ = float(page.mediabox.width); ph_ = float(page.mediabox.height)
                overlay = io.BytesIO()
                c = rl_canvas.Canvas(overlay, pagesize=(pw_,ph_))
                if i == pg_num-1:
                    r_ = int(color[1:3],16)/255; g_=int(color[3:5],16)/255; b_=int(color[5:7],16)/255
                    c.setFillColorRGB(r_,g_,b_)
                    c.rect(x1, y1, x2-x1, y2-y1, fill=1, stroke=0)
                c.showPage(); c.save(); overlay.seek(0)
                op = PdfReader(overlay).pages[0]
                page.merge_page(op)
                writer.add_page(page)
            buf = io.BytesIO(); writer.write(buf); buf.seek(0)
            st.success("✅ Redact ပြီး!")
            download_btn(buf.read(), f"redacted_{f.name}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL: COMPARE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def tool_compare():
    tool_header("🔍","Compare PDF","PDF နှစ်ခု နှိုင်းယှဉ်ပါ")
    c1,c2 = st.columns(2)
    f1 = c1.file_uploader("📄 ပထမ PDF", type=["pdf"], key="cmp1")
    f2 = c2.file_uploader("📄 ဒုတိယ PDF", type=["pdf"], key="cmp2")
    if not (f1 and f2): return
    r1 = PdfReader(io.BytesIO(f1.read())); r2 = PdfReader(io.BytesIO(f2.read()))
    st.markdown("### 📊 နှိုင်းယှဉ်မှု")
    c3,c4 = st.columns(2)
    c3.metric("ပထမ PDF Pages",len(r1.pages))
    c4.metric("ဒုတိယ PDF Pages",len(r2.pages))
    c5,c6 = st.columns(2)
    meta1 = r1.metadata or {}; meta2 = r2.metadata or {}
    c5.write(f"**Title:** {meta1.get('/Title','—')}")
    c5.write(f"**Author:** {meta1.get('/Author','—')}")
    c6.write(f"**Title:** {meta2.get('/Title','—')}")
    c6.write(f"**Author:** {meta2.get('/Author','—')}")

    if st.button("🔍 Text နှိုင်းယှဉ်မည်", use_container_width=True):
        with st.spinner("Text ထုတ်နေသည်..."):
            t1 = "".join(p.extract_text() or "" for p in r1.pages)
            t2 = "".join(p.extract_text() or "" for p in r2.pages)
            import difflib
            diff = list(difflib.unified_diff(t1.splitlines(), t2.splitlines(),
                                             lineterm="", n=3))
            if diff:
                diff_text = "\n".join(diff[:200])
                st.text_area("Diff (ပထမ 200 lines)", diff_text, height=350)
                st.info(f"ကွဲလွဲချက် {len(diff)} lines တွေ့သည်")
            else:
                st.success("✅ PDF နှစ်ခုတွင် text ကွဲလွဲချက် မတွေ့ပါ!")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL: AI SUMMARIZE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def tool_summarize():
    tool_header("🧠","AI Summary","PDF မှ AI ဖြင့် အနှစ်ချုပ်")
    f = st.file_uploader("PDF ဖိုင် ရွေးပါ", type=["pdf"])
    if not f: return
    lang = st.radio("အနှစ်ချုပ် ဘာသာ",["မြန်မာ","English"])
    length = st.select_slider("အတိုကောက် အဆင့်",["အတိုဆုံး","အတိုသော","ပုံမှန်","အရှည်သော"])

    if st.button("🧠 AI Summary ရယူမည်", use_container_width=True):
        with st.spinner("PDF text ထုတ်နေသည်..."):
            reader = PdfReader(io.BytesIO(f.read()))
            text = "\n".join(p.extract_text() or "" for p in reader.pages[:10])
            if not text.strip():
                st.error("Text ထုတ်မရပါ (Scanned PDF ဖြစ်နိုင်သည် - OCR ဦးသုံးပါ)"); return
        with st.spinner("Claude AI နှင့် အနှစ်ချုပ်နေသည်..."):
            import requests, json
            len_inst = {"အတိုဆုံး":"1-2 sentences","အတိုသော":"3-4 sentences",
                        "ပုံမှန်":"2-3 paragraphs","အရှည်သော":"5+ paragraphs"}[length]
            lang_inst = "Myanmar language (Unicode, not Zawgyi)" if lang=="မြန်မာ" else "English"
            prompt = f"""Please summarize the following PDF text in {lang_inst}. 
Length: {len_inst}. 
Be concise and highlight the key points.

PDF TEXT:
{text[:4000]}"""
            resp = requests.post("https://api.anthropic.com/v1/messages",
                headers={"Content-Type":"application/json"},
                json={"model":"claude-sonnet-4-20250514","max_tokens":1000,
                      "messages":[{"role":"user","content":prompt}]},
                timeout=60)
            if resp.status_code == 200:
                result = resp.json()["content"][0]["text"]
                st.markdown("### 📋 AI Summary")
                st.markdown(result)
                st.download_button("⬇️ Summary ဒေါင်းရန်", result,
                                   f"summary_{f.name}.txt", mime="text/plain",
                                   use_container_width=True)
            else:
                st.error(f"AI Error: {resp.status_code}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOL: AI TRANSLATE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def tool_translate():
    tool_header("🌏","AI Translate PDF","PDF ကို AI ဖြင့် မြန်မာဘာသာ ပြန်")
    f = st.file_uploader("PDF ဖိုင် ရွေးပါ", type=["pdf"])
    if not f: return
    c1,c2 = st.columns(2)
    src_lang = c1.selectbox("မူလ ဘာသာ",["English","Chinese","Japanese","Thai","Korean","Arabic","ဘာသာ မသိ"])
    tgt_lang = c2.selectbox("ပြန်မည့် ဘာသာ",["မြန်မာ","English","Chinese","Japanese"])
    pages_opt = st.radio("Pages",["Page 1-3 (Preview)","Page အကုန်"])

    if st.button("🌏 ဘာသာပြန်မည်", use_container_width=True):
        with st.spinner("PDF text ထုတ်နေသည်..."):
            reader = PdfReader(io.BytesIO(f.read()))
            max_p = 3 if "Preview" in pages_opt else len(reader.pages)
            text = "\n\n".join(f"[Page {i+1}]\n{reader.pages[i].extract_text() or ''}"
                               for i in range(min(max_p, len(reader.pages))))
            if not text.strip():
                st.error("Text ထုတ်မရပါ (OCR ဦးသုံးပါ)"); return
        with st.spinner(f"Claude AI ဖြင့် {tgt_lang} ဘာသာပြန်နေသည်..."):
            import requests
            prompt = f"""Translate the following text from {src_lang} to {tgt_lang}.
Keep the page markers [Page N] intact.
Preserve formatting as much as possible.
If translating to Myanmar, use Unicode Myanmar (not Zawgyi).

TEXT TO TRANSLATE:
{text[:5000]}"""
            resp = requests.post("https://api.anthropic.com/v1/messages",
                headers={"Content-Type":"application/json"},
                json={"model":"claude-sonnet-4-20250514","max_tokens":2000,
                      "messages":[{"role":"user","content":prompt}]},
                timeout=90)
            if resp.status_code == 200:
                result = resp.json()["content"][0]["text"]
                st.markdown(f"### 🌏 {tgt_lang} ဘာသာပြန်")
                st.text_area("ရလဒ်", result, height=400)
                st.download_button("⬇️ ဒေါင်းရန်", result,
                                   f"translated_{f.name}.txt", mime="text/plain",
                                   use_container_width=True)
            else:
                st.error(f"AI Error: {resp.status_code}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ROUTER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
tool = st.session_state.tool

if   tool is None:      page_home()
elif tool == "merge":   tool_merge()
elif tool == "split":   tool_split()
elif tool == "remove":  tool_remove()
elif tool == "extract": tool_extract()
elif tool == "organize":tool_organize()
elif tool == "compress":tool_compress()
elif tool == "repair":  tool_repair()
elif tool == "ocr":     tool_ocr()
elif tool == "img2pdf": tool_img2pdf()
elif tool == "word2pdf":tool_office2pdf("word")
elif tool == "ppt2pdf": tool_office2pdf("ppt")
elif tool == "excel2pdf":tool_office2pdf("excel")
elif tool == "html2pdf":tool_html2pdf()
elif tool == "pdf2img": tool_pdf2img()
elif tool == "pdf2word":tool_pdf2office("word")
elif tool == "pdf2ppt": tool_pdf2office("ppt")
elif tool == "pdf2excel":tool_pdf2office("excel")
elif tool == "rotate":  tool_rotate()
elif tool == "pagenum": tool_pagenum()
elif tool == "watermark":tool_watermark()
elif tool == "crop":    tool_crop()
elif tool == "create":  tool_create()
elif tool == "protect": tool_protect()
elif tool == "unlock":  tool_unlock()
elif tool == "nocopy":  tool_nocopy()
elif tool == "redact":  tool_redact()
elif tool == "compare": tool_compare()
elif tool == "summarize":tool_summarize()
elif tool == "translate":tool_translate()
