import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
#  Page Config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Myanmar Auditor Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
#  Custom CSS  —  Gold / Navy / Cream theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Source+Sans+3:wght@300;400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Source Sans 3', sans-serif;
    }

    .stApp {
        background-color: #0e1420;
        color: #e8dfc8;
    }
    .main .block-container {
        padding: 2rem 2.8rem;
        max-width: 1440px;
    }

    /* ── Header Banner ── */
    .audit-header {
        background: linear-gradient(135deg, #1a2240 0%, #111827 60%, #0e1420 100%);
        border: 1px solid #c9a84c;
        border-radius: 14px;
        padding: 2.2rem 2.8rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    .audit-header::before {
        content: '';
        position: absolute;
        top: -60px; right: -60px;
        width: 280px; height: 280px;
        background: radial-gradient(circle, rgba(201,168,76,0.12) 0%, transparent 70%);
        border-radius: 50%;
    }
    .audit-header h1 {
        font-family: 'Playfair Display', serif;
        font-size: 2rem;
        font-weight: 700;
        color: #c9a84c;
        margin: 0 0 0.4rem 0;
        text-shadow: 0 2px 12px rgba(201,168,76,0.2);
    }
    .audit-header p { color: #8a96aa; margin: 0; font-size: 0.95rem; font-weight: 300; }
    .audit-header .vtag {
        position: absolute; top: 1.5rem; right: 2rem;
        background: rgba(201,168,76,0.12);
        border: 1px solid rgba(201,168,76,0.3);
        color: #c9a84c;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        padding: 0.25rem 0.7rem;
        border-radius: 20px; letter-spacing: 1px;
    }

    /* ── Section Title ── */
    .section-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem; font-weight: 600;
        letter-spacing: 2.5px; text-transform: uppercase;
        color: #c9a84c;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid #1e2a42;
        margin-bottom: 1.2rem;
    }

    /* ── Metric Cards ── */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 0.8rem; margin-bottom: 1.8rem;
    }
    .metric-card {
        background: linear-gradient(145deg, #131d30, #0e1420);
        border: 1px solid #1e2a42;
        border-radius: 12px;
        padding: 1.1rem 1.3rem;
        position: relative; overflow: hidden;
        transition: border-color 0.25s, transform 0.2s;
    }
    .metric-card::before {
        content: ''; position: absolute;
        top: 0; left: 0; right: 0; height: 3px;
        border-radius: 12px 12px 0 0;
    }
    .metric-card:hover { border-color: #c9a84c; transform: translateY(-2px); }
    .metric-card.gold::before  { background: linear-gradient(90deg,#c9a84c,#f0d080); }
    .metric-card.green::before { background: linear-gradient(90deg,#4caf7d,#6ee09b); }
    .metric-card.red::before   { background: linear-gradient(90deg,#e05252,#f08080); }
    .metric-card.amber::before { background: linear-gradient(90deg,#e0943a,#f0b860); }
    .metric-card.blue::before  { background: linear-gradient(90deg,#4a7fc1,#7aaee0); }
    .metric-card .label { font-size:0.7rem; color:#5a6880; letter-spacing:0.8px; text-transform:uppercase; margin-bottom:0.5rem; }
    .metric-card .value { font-family:'JetBrains Mono',monospace; font-size:1.75rem; font-weight:600; line-height:1; }
    .metric-card.gold  .value { color:#c9a84c; }
    .metric-card.green .value { color:#4caf7d; }
    .metric-card.red   .value { color:#e05252; }
    .metric-card.amber .value { color:#e0943a; }
    .metric-card.blue  .value { color:#4a7fc1; }
    .metric-card .sub { font-size:0.71rem; color:#5a6880; margin-top:0.3rem; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg,#111827 0%,#0e1420 100%) !important;
        border-right: 1px solid #1e2a42;
    }
    [data-testid="stSidebar"] .stMarkdown p { color:#5a6880; font-size:0.83rem; }

    /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg,#c9a84c 0%,#a8862e 100%);
        color: #0e1420; border: none; border-radius: 9px;
        font-weight: 700; font-size: 0.92rem;
        padding: 0.65rem 2rem; letter-spacing: 0.3px;
        transition: all 0.25s; width: 100%;
        box-shadow: 0 2px 12px rgba(201,168,76,0.2);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 24px rgba(201,168,76,0.35);
    }

    .stDownloadButton > button {
        background: #131d30 !important;
        color: #c9a84c !important;
        border: 1px solid #c9a84c !important;
        border-radius: 9px; font-weight: 600;
        transition: all 0.2s;
    }
    .stDownloadButton > button:hover {
        background: rgba(201,168,76,0.1) !important;
        box-shadow: 0 4px 16px rgba(201,168,76,0.2);
    }

    .streamlit-expanderHeader {
        background: #131d30 !important;
        border: 1px solid #1e2a42 !important;
        border-radius: 8px; color: #e8dfc8 !important;
    }
    .stDataFrame { border:1px solid #1e2a42; border-radius:10px; overflow:hidden; }
    .stSelectbox > div > div,
    .stMultiSelect > div,
    .stNumberInput input,
    .stTextInput input {
        background: #131d30 !important;
        border-color: #1e2a42 !important;
        color: #e8dfc8 !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: #131d30;
        border-radius: 10px 10px 0 0;
        border-bottom: 2px solid #1e2a42; gap: 0;
    }
    .stTabs [data-baseweb="tab"] {
        color: #5a6880; font-weight: 600; font-size: 0.85rem;
        letter-spacing: 0.3px; padding: 0.75rem 1.6rem;
    }
    .stTabs [aria-selected="true"] {
        color: #c9a84c !important;
        border-bottom: 2px solid #c9a84c !important;
        background: transparent !important;
    }

    .info-box {
        background: #131d30; border: 1px solid #1e2a42;
        border-radius: 11px; padding: 1.4rem 1.6rem; margin: 0.8rem 0;
    }
    .info-box.gold  { border-left: 3px solid #c9a84c; }
    .info-box.green { border-left: 3px solid #4caf7d; }
    .info-box.red   { border-left: 3px solid #e05252; }
    .info-box.amber { border-left: 3px solid #e0943a; }

    .stCheckbox label span { color: #b0b8c8; font-size: 0.88rem; }
    hr { border-color: #1e2a42; }
    .stSuccess { background:#0f2a1e; border-left-color:#4caf7d; }
    .stInfo    { background:#0e1e35; border-left-color:#4a7fc1; }
    .stWarning { background:#2a1e0e; border-left-color:#e0943a; }
    .stError   { background:#2a0e0e; border-left-color:#e05252; }

    [data-testid="stFileUploadDropzone"] {
        background: #131d30 !important;
        border: 1.5px dashed #1e2a42 !important;
        border-radius: 10px;
    }
    [data-testid="stFileUploadDropzone"]:hover {
        border-color: #c9a84c !important;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  Header
# ─────────────────────────────────────────────
st.markdown("""
<div class="audit-header">
    <span class="vtag">v3.0</span>
    <h1>📊 Myanmar Auditor Pro</h1>
    <p>Advanced Excel / CSV Reconciliation &amp; Audit Tool — XLOOKUP Style Variance Detection</p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  Helper Functions
# ─────────────────────────────────────────────

def detect_encoding(raw_bytes):
    """Detect encoding without chardet — BOM check then safe fallback."""
    if raw_bytes[:3] == b'\xef\xbb\xbf':
        return 'utf-8-sig'
    if raw_bytes[:2] in (b'\xff\xfe', b'\xfe\xff'):
        return 'utf-16'
    try:
        raw_bytes[:50000].decode('utf-8')
        return 'utf-8'
    except UnicodeDecodeError:
        return 'cp1252'


def load_file(file, sheet_idx=0, header_row=0, skip_rows=0):
    """
    Smart multi-engine loader.
    Handles .xlsx, .xls, .csv — including OLE2/corrupt Excel errors.
    Returns (dataframe, error_message, file_type_string)
    """
    if file is None:
        return None, "No file provided.", None

    name = file.name.lower()
    raw  = file.read()
    file.seek(0)
    skip = skip_rows if skip_rows > 0 else None

    # ── CSV ───────────────────────────────────
    if name.endswith('.csv'):
        for enc in [detect_encoding(raw), 'utf-8', 'utf-8-sig', 'cp1252', 'latin-1']:
            try:
                df = pd.read_csv(io.BytesIO(raw), encoding=enc,
                                 skiprows=skip, header=header_row, on_bad_lines='skip')
                df.columns = [str(c).strip() for c in df.columns]
                return df, None, 'csv'
            except Exception:
                continue
        return None, "CSV ဖတ်မရပါ။ File encoding စစ်ဆေးပြီး ထပ်ကြိုးစားပါ။", None

    # ── Excel ─────────────────────────────────
    if name.endswith(('.xlsx', '.xls', '.xlsm')):
        engines  = ['openpyxl', 'xlrd']
        ft_label = 'xlsx' if name.endswith('.xlsx') else 'xls'
        last_err = ''

        for engine in engines:
            try:
                df = pd.read_excel(io.BytesIO(raw), sheet_name=sheet_idx,
                                   header=header_row, skiprows=skip, engine=engine)
                df.columns = [str(c).strip() for c in df.columns]
                return df, None, ft_label
            except Exception as e:
                last_err = str(e)
                continue

        # calamine fallback (very broad compatibility)
        try:
            df = pd.read_excel(io.BytesIO(raw), sheet_name=sheet_idx,
                               header=header_row, skiprows=skip, engine='calamine')
            df.columns = [str(c).strip() for c in df.columns]
            return df, None, ft_label
        except Exception as e:
            last_err = str(e)

        # Last resort: try as CSV (some web-exported "xlsx" are HTML/CSV)
        for enc in [detect_encoding(raw), 'utf-8', 'utf-8-sig', 'cp1252', 'latin-1']:
            try:
                df = pd.read_csv(io.BytesIO(raw), encoding=enc, on_bad_lines='skip')
                df.columns = [str(c).strip() for c in df.columns]
                st.warning(
                    "⚠️ File ကို Excel format အနေနဲ့ ဖတ်မရ၍ CSV အနေနဲ့ ဖတ်ပါသည်။  "
                    "File ကို Excel မှာ Re-save လုပ်ကြည့်ပါ။"
                )
                return df, None, 'csv_fallback'
            except Exception:
                continue

        # All engines failed — return friendly Myanmar error
        err = (
            "**Excel ဖိုင် ဖတ်မရပါ (OLE2 / Format Error)**\n\n"
            "**ဖြေရှင်းနည်းများ —**\n"
            "1. ဖိုင်ကို Excel Program မှာ ဖွင့်ပြီး `File → Save As → Excel Workbook (.xlsx)` Re-save လုပ်ပါ\n"
            "2. CSV format ဆိုရင် `.csv` extension နဲ့ save လုပ်ပြီး တင်ပါ\n"
            "3. Google Sheets မှာ ဖွင့်ပြီး `File → Download → .xlsx` ပြန် download ယူပါ\n"
            "4. ဖိုင်ပျက်နေရင် original source ကနေ ထပ်ရယူပါ\n\n"
            f"_(Technical: {last_err})_"
        )
        return None, err, None

    return None, (
        f"Unsupported format: `{name}`\n"
        "`.xlsx` · `.xls` · `.csv` သာ လက်ခံပါသည်။"
    ), None


def detect_duplicates(df, key_col):
    return df[df.duplicated(subset=[key_col], keep=False)].copy()


def compute_summary(df_result, amt_src, amt_tgt):
    total       = len(df_result)
    matched     = (df_result['Audit_Status'] == 'Matched ✓').sum()
    miss_src    = (df_result['Audit_Status'] == 'Missing in Source').sum()
    miss_tgt    = (df_result['Audit_Status'] == 'Missing in Target').sum()
    discrepancy = (df_result['Audit_Status'] == 'Amount Discrepancy').sum()
    src_total   = df_result[amt_src].fillna(0).sum()
    tgt_total   = df_result[amt_tgt].fillna(0).sum()
    total_var   = df_result['Variance'].sum()
    pct         = (matched / total * 100) if total > 0 else 0
    return dict(total=total, matched=matched, miss_src=miss_src, miss_tgt=miss_tgt,
                discrepancy=discrepancy, src_total=src_total, tgt_total=tgt_total,
                total_variance=total_var, pct_matched=pct)


def get_status(row, src_col, tgt_col, tolerance):
    if pd.isna(row[src_col]): return 'Missing in Source'
    if pd.isna(row[tgt_col]): return 'Missing in Target'
    if abs(row['Variance']) > tolerance: return 'Amount Discrepancy'
    return 'Matched ✓'


def style_status(val):
    m = {
        'Matched ✓':          'background-color:#0f2a1e;color:#4caf7d',
        'Missing in Source':  'background-color:#2a1e0e;color:#e0943a',
        'Missing in Target':  'background-color:#1a1535;color:#9b7fe8',
        'Amount Discrepancy': 'background-color:#2a0e0e;color:#e05252',
    }
    return m.get(val, '')


def style_variance(val):
    try:
        v = float(val)
        if v > 0: return 'color:#e05252'
        if v < 0: return 'color:#e0943a'
        return 'color:#4caf7d'
    except:
        return ''


def to_excel_bytes(df_main, summary_stats):
    """4-sheet styled Excel export with full conditional formatting."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        wb = writer.book

        # Palette
        NAVY   = '#111827'; GOLD  = '#c9a84c'; CREAM = '#e8dfc8'
        DARK   = '#0e1420'; PANEL = '#131d30'; BORD  = '#1e2a42'
        GREEN  = '#4caf7d'; RED   = '#e05252'
        AMBER  = '#e0943a'; PURP  = '#9b7fe8'

        def f(**kw):
            base = dict(font_name='Calibri', font_size=10, font_color=CREAM,
                        bg_color=PANEL, border=1, border_color=BORD)
            base.update(kw)
            return wb.add_format(base)

        title_f  = f(font_size=15, bold=True, font_color=GOLD, bg_color=DARK, border=0)
        sub_f    = f(font_size=9,  font_color='#5a6880', bg_color=DARK, border=0)
        hdr_f    = f(bold=True, font_color=GOLD, bg_color=NAVY,
                     align='center', valign='vcenter', text_wrap=True)
        ok_f     = f(font_color=GREEN, bg_color='#0a1e14', bold=True)
        ms_f     = f(font_color=AMBER, bg_color='#1e1408')
        mt_f     = f(font_color=PURP,  bg_color='#110e22')
        disc_f   = f(font_color=RED,   bg_color='#1e0808', bold=True)
        var_pos  = f(font_color=RED,   bg_color='#1e0808', num_format='#,##0.00', bold=True)
        var_neg  = f(font_color=AMBER, bg_color=PANEL,     num_format='#,##0.00')
        var_zero = f(font_color='#5a6880', bg_color=PANEL, num_format='#,##0.00')
        kv_key   = f(bold=True, font_color=GOLD, bg_color=NAVY,  align='left')
        kv_val   = f(font_color=CREAM, bg_color=PANEL, align='right')
        kv_pos_v = f(font_color=RED,   bg_color=PANEL, align='right', num_format='#,##0.00')
        kv_neg_v = f(font_color=AMBER, bg_color=PANEL, align='right', num_format='#,##0.00')
        sec_f    = f(bold=True, italic=True, font_color='#5a6880', bg_color=DARK, border=0)

        sfmt = {'Matched ✓': ok_f, 'Missing in Source': ms_f,
                'Missing in Target': mt_f, 'Amount Discrepancy': disc_f}

        def write_title(ws, title, sub=''):
            ws.write(0, 0, title, title_f)
            if sub: ws.write(1, 0, sub, sub_f)
            ws.set_row(0, 24); ws.set_row(1, 16)

        def write_hdrs(ws, cols, row=3):
            for ci, cn in enumerate(cols):
                ws.write(row, ci, cn, hdr_f)
                ws.set_column(ci, ci, max(len(str(cn)) + 4, 14))

        def write_data_rows(ws, df, start_row=4, var_col=None, status_col=None):
            for ri, (_, rd) in enumerate(df.iterrows()):
                er = ri + start_row
                status = rd.get('Audit_Status', '')
                base   = sfmt.get(status, f())
                for ci, val in enumerate(rd):
                    v = val if not pd.isna(val) else ''
                    ws.write(er, ci, v, base)
                if status_col is not None:
                    ws.write(er, status_col, status, sfmt.get(status, f()))
                if var_col is not None:
                    vv = rd.get('Variance', 0) or 0
                    vf = var_pos if vv > 0 else (var_neg if vv < 0 else var_zero)
                    ws.write(er, var_col, vv, vf)

        # ── Sheet 1: Full Report ──────────────
        df_main.to_excel(writer, index=False, sheet_name='Audit_Report', startrow=3)
        ws1 = writer.sheets['Audit_Report']
        ws1.set_tab_color(GOLD)
        write_title(ws1, '  Myanmar Auditor Pro — Full Audit Report',
                    f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        write_hdrs(ws1, df_main.columns)
        cols_list = list(df_main.columns)
        sc = cols_list.index('Audit_Status') if 'Audit_Status' in cols_list else None
        vc = cols_list.index('Variance')     if 'Variance'     in cols_list else None
        write_data_rows(ws1, df_main, start_row=4, var_col=vc, status_col=sc)
        ws1.freeze_panes(4, 0)
        ws1.autofilter(3, 0, 3 + len(df_main), len(df_main.columns) - 1)
        ws1.set_zoom(90)

        # ── Sheet 2: Summary ──────────────────
        ws2 = wb.add_worksheet('Summary')
        ws2.set_tab_color(GREEN)
        ws2.set_column(0, 0, 34); ws2.set_column(1, 1, 22)
        ws2.set_zoom(110)
        write_title(ws2, '  Audit Summary Dashboard',
                    f'Myanmar Auditor Pro  |  {datetime.now().strftime("%Y-%m-%d %H:%M")}')

        rows = [
            ('── Audit Scope ─────────────────────', ''),
            ('Report Generated',        datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('Total Records (merged)',   summary_stats['total']),
            ('', ''),
            ('── Match Results ───────────────────', ''),
            ('Matched',                  summary_stats['matched']),
            ('Missing in Source',        summary_stats['miss_src']),
            ('Missing in Target',        summary_stats['miss_tgt']),
            ('Amount Discrepancy',       summary_stats['discrepancy']),
            ('Match Rate (%)',           f"{summary_stats['pct_matched']:.2f}%"),
            ('', ''),
            ('── Financial Summary ───────────────', ''),
            ('Source Total',             summary_stats['src_total']),
            ('Target Total',             summary_stats['tgt_total']),
            ('Net Variance (Src − Tgt)', summary_stats['total_variance']),
        ]
        for i, (k, v) in enumerate(rows, start=3):
            if not k and not v:
                ws2.write(i, 0, '', f(bg_color=DARK, border=0))
                ws2.write(i, 1, '', f(bg_color=DARK, border=0))
            elif str(k).startswith('──'):
                ws2.write(i, 0, k, sec_f)
                ws2.write(i, 1, '', sec_f)
            else:
                ws2.write(i, 0, k, kv_key)
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    if 'Variance' in k:
                        vf = kv_pos_v if v > 0 else (kv_neg_v if v < 0 else kv_val)
                    else:
                        vf = kv_val
                    ws2.write(i, 1, v, vf)
                else:
                    ws2.write(i, 1, str(v), kv_val)

        # ── Sheet 3: Issues Only ──────────────
        df_issues = df_main[df_main['Audit_Status'] != 'Matched ✓'].copy()
        df_issues.to_excel(writer, index=False, sheet_name='Issues_Only', startrow=3)
        ws3 = writer.sheets['Issues_Only']
        ws3.set_tab_color(RED)
        write_title(ws3, f'  Issues Only — {len(df_issues):,} records',
                    'Discrepancies · Missing Source · Missing Target')
        write_hdrs(ws3, df_issues.columns)
        sc3 = list(df_issues.columns).index('Audit_Status') if 'Audit_Status' in df_issues.columns else None
        vc3 = list(df_issues.columns).index('Variance')     if 'Variance'     in df_issues.columns else None
        write_data_rows(ws3, df_issues, start_row=4, var_col=vc3, status_col=sc3)
        ws3.freeze_panes(4, 0)
        ws3.autofilter(3, 0, 3 + len(df_issues), len(df_issues.columns) - 1)

        # ── Sheet 4: Matched Only ─────────────
        df_ok = df_main[df_main['Audit_Status'] == 'Matched ✓'].copy()
        df_ok.to_excel(writer, index=False, sheet_name='Matched_Only', startrow=3)
        ws4 = writer.sheets['Matched_Only']
        ws4.set_tab_color(GREEN)
        write_title(ws4, f'  Matched Records — {len(df_ok):,} records',
                    'All records that reconcile perfectly')
        write_hdrs(ws4, df_ok.columns)
        for ri, (_, rd) in enumerate(df_ok.iterrows()):
            for ci, val in enumerate(rd):
                ws4.write(ri + 4, ci, val if not pd.isna(val) else '', ok_f)
        ws4.freeze_panes(4, 0)

    return output.getvalue()


# ─────────────────────────────────────────────
#  Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-title">📁 File Upload</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#5a6880;font-size:0.8rem;margin-bottom:0.5rem;">xlsx · xls · csv လက်ခံပါသည်</p>', unsafe_allow_html=True)

    source_file = st.file_uploader("📂 Source File (Cash Book / GL)",
                                   type=['xlsx','xls','csv'],
                                   help="စစ်ဆေးမည့် ဖိုင်")
    target_file = st.file_uploader("📂 Target File (Bank / Master)",
                                   type=['xlsx','xls','csv'],
                                   help="အတည်ပြုမည့် ဖိုင်")

    st.markdown('<div class="section-title" style="margin-top:1.5rem;">⚙️ File Settings</div>', unsafe_allow_html=True)

    with st.expander("Source File Settings"):
        src_sheet  = st.number_input("Sheet Index (0-based)", min_value=0, value=0, key='ss')
        src_header = st.number_input("Header Row",            min_value=0, value=0, key='sh')
        src_skip   = st.number_input("Skip Rows",             min_value=0, value=0, key='sk')

    with st.expander("Target File Settings"):
        tgt_sheet  = st.number_input("Sheet Index (0-based)", min_value=0, value=0, key='ts')
        tgt_header = st.number_input("Header Row",            min_value=0, value=0, key='th')
        tgt_skip   = st.number_input("Skip Rows",             min_value=0, value=0, key='tk')

    st.markdown('<div class="section-title" style="margin-top:1rem;">🛡 Audit Rules</div>', unsafe_allow_html=True)

    with st.expander("Matching Rules"):
        tolerance    = st.number_input("Variance Tolerance (±)", min_value=0.0, value=0.0, step=0.01)
        case_sens    = st.checkbox("Case-sensitive Key Matching", value=False)
        strip_spaces = st.checkbox("Strip Whitespace from Keys",  value=True)
        flag_dups    = st.checkbox("Flag Duplicate Keys",         value=True)

    st.markdown("---")
    st.markdown('<p style="color:#5a6880;font-size:0.75rem;">Myanmar Auditor Pro v3.0<br>Streamlit · Pandas · XlsxWriter</p>',
                unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  Welcome Screen
# ─────────────────────────────────────────────
if not (source_file and target_file):
    st.markdown("""
    <div class="info-box gold">
        <h4 style="color:#c9a84c;margin:0 0 0.6rem 0;font-family:'Playfair Display',serif;">🚀 Getting Started</h4>
        <p style="color:#8a96aa;margin:0;line-height:1.7;">
            Sidebar မှာ Excel / CSV ဖိုင် ၂ ခု Upload လုပ်ပါ —
            <strong style="color:#e8dfc8;">Source</strong> (Cash Book / GL) နှင့်
            <strong style="color:#e8dfc8;">Target</strong> (Bank Statement / Master).<br><br>
            <strong style="color:#c9a84c;">✦ Supported Formats:</strong>
            <code style="background:#1e2a42;padding:2px 6px;border-radius:4px;">.xlsx</code>
            <code style="background:#1e2a42;padding:2px 6px;border-radius:4px;">.xls</code>
            <code style="background:#1e2a42;padding:2px 6px;border-radius:4px;">.csv</code>
            &nbsp;(Auto encoding detection · OLE2 error auto-recovery)<br><br>
            <strong style="color:#c9a84c;">✦ Features:</strong>
            Multi-engine Excel loading · Duplicate detection · Variance tolerance ·
            4-sheet styled Excel export · CSV export (UTF-8 BOM)
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ─────────────────────────────────────────────
#  Load Files
# ─────────────────────────────────────────────
df_src, err_src, ftype_src = load_file(source_file, src_sheet, src_header, src_skip)
df_tgt, err_tgt, ftype_tgt = load_file(target_file, tgt_sheet, tgt_header, tgt_skip)

if err_src:
    st.error(err_src)
    st.stop()
if err_tgt:
    st.error(err_tgt)
    st.stop()

ft_label = {'xlsx':'Excel (.xlsx)','xls':'Excel (.xls)','csv':'CSV','csv_fallback':'CSV (fallback)'}
fl_src = ft_label.get(ftype_src, ftype_src)
fl_tgt = ft_label.get(ftype_tgt, ftype_tgt)


# ─────────────────────────────────────────────
#  Data Preview
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">📋 Data Preview</div>', unsafe_allow_html=True)
p1, p2 = st.columns(2)
with p1:
    st.caption(f"**Source** [{fl_src}] — {len(df_src):,} rows × {len(df_src.columns)} columns")
    st.dataframe(df_src.head(8), use_container_width=True, height=240)
with p2:
    st.caption(f"**Target** [{fl_tgt}] — {len(df_tgt):,} rows × {len(df_tgt.columns)} columns")
    st.dataframe(df_tgt.head(8), use_container_width=True, height=240)

st.divider()


# ─────────────────────────────────────────────
#  Audit Configuration
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">🛠 Audit Configuration</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1: src_key = st.selectbox("Source Key Column",   options=df_src.columns)
with c2: tgt_key = st.selectbox("Target Key Column",   options=df_tgt.columns)
with c3: src_amt = st.selectbox("Source Amount Column",options=df_src.columns)
with c4: tgt_amt = st.selectbox("Target Amount Column",options=df_tgt.columns)

ec1, ec2 = st.columns(2)
with ec1:
    extra_src = st.multiselect("Extra Source Columns",
                               [c for c in df_src.columns if c not in [src_key, src_amt]])
with ec2:
    extra_tgt = st.multiselect("Extra Target Columns",
                               [c for c in df_tgt.columns if c not in [tgt_key, tgt_amt]])

st.markdown("")
run_btn = st.button("▶  Run Full Audit Process")


# ─────────────────────────────────────────────
#  Run Audit
# ─────────────────────────────────────────────
if run_btn:
    with st.spinner("Auditing data…"):
        src = df_src[[src_key, src_amt] + extra_src].copy()
        tgt = df_tgt[[tgt_key, tgt_amt] + extra_tgt].copy()

        if strip_spaces:
            src[src_key] = src[src_key].astype(str).str.strip()
            tgt[tgt_key] = tgt[tgt_key].astype(str).str.strip()
        if not case_sens:
            src[src_key] = src[src_key].astype(str).str.upper()
            tgt[tgt_key] = tgt[tgt_key].astype(str).str.upper()

        dup_src = detect_duplicates(src, src_key) if flag_dups else pd.DataFrame()
        dup_tgt = detect_duplicates(tgt, tgt_key) if flag_dups else pd.DataFrame()

        src_r = src.rename(columns={src_key: '_KEY_', src_amt: src_amt + '_Source'})
        tgt_r = tgt.rename(columns={tgt_key: '_KEY_', tgt_amt: tgt_amt + '_Target'})
        for c in extra_src: src_r = src_r.rename(columns={c: c + '_Src'})
        for c in extra_tgt: tgt_r = tgt_r.rename(columns={c: c + '_Tgt'})

        merged = pd.merge(src_r, tgt_r, on='_KEY_', how='outer')
        merged.rename(columns={'_KEY_': src_key}, inplace=True)

        s_col = src_amt + '_Source'
        t_col = tgt_amt + '_Target'
        merged['Variance']   = merged[s_col].fillna(0) - merged[t_col].fillna(0)
        merged['Variance_%'] = merged.apply(
            lambda r: (r['Variance'] / r[t_col] * 100)
            if (pd.notna(r[t_col]) and r[t_col] != 0) else np.nan, axis=1)
        merged['Audit_Status'] = merged.apply(
            lambda r: get_status(r, s_col, t_col, tolerance), axis=1)

        stats = compute_summary(merged, s_col, t_col)

    # ── Success ────────────────────────────────
    st.success(f"✅ Audit Complete — {stats['total']:,} records processed  |  {datetime.now().strftime('%H:%M:%S')}")

    # ── Metrics ────────────────────────────────
    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-card gold">
            <div class="label">Total Records</div>
            <div class="value">{stats['total']:,}</div>
            <div class="sub">after outer merge</div>
        </div>
        <div class="metric-card green">
            <div class="label">Matched ✓</div>
            <div class="value">{stats['matched']:,}</div>
            <div class="sub">{stats['pct_matched']:.1f}% match rate</div>
        </div>
        <div class="metric-card red">
            <div class="label">Discrepancies</div>
            <div class="value">{stats['discrepancy']:,}</div>
            <div class="sub">amount mismatch</div>
        </div>
        <div class="metric-card amber">
            <div class="label">Missing Items</div>
            <div class="value">{stats['miss_src'] + stats['miss_tgt']:,}</div>
            <div class="sub">src {stats['miss_src']} · tgt {stats['miss_tgt']}</div>
        </div>
        <div class="metric-card blue">
            <div class="label">Net Variance</div>
            <div class="value">{stats['total_variance']:,.0f}</div>
            <div class="sub">source − target</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Duplicates ─────────────────────────────
    if flag_dups and (len(dup_src) > 0 or len(dup_tgt) > 0):
        with st.expander(f"⚠️ Duplicate Keys — Source: {len(dup_src)} · Target: {len(dup_tgt)}"):
            d1, d2 = st.columns(2)
            with d1:
                st.caption("Source Duplicates")
                st.dataframe(dup_src, use_container_width=True) if len(dup_src) else st.success("None")
            with d2:
                st.caption("Target Duplicates")
                st.dataframe(dup_tgt, use_container_width=True) if len(dup_tgt) else st.success("None")

    # ── Tabs ───────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Full Report", "❌ Issues Only", "✅ Matched", "🔍 Missing", "📈 Analytics"
    ])

    with tab1:
        st.caption(f"All {len(merged):,} records")
        st.dataframe(merged.style
                     .applymap(style_status,   subset=['Audit_Status'])
                     .applymap(style_variance, subset=['Variance']),
                     use_container_width=True, height=460)

    with tab2:
        issues = merged[merged['Audit_Status'] != 'Matched ✓']
        st.caption(f"{len(issues):,} issues")
        if len(issues):
            st.dataframe(issues.style.applymap(style_status, subset=['Audit_Status']),
                         use_container_width=True, height=430)
        else:
            st.success("🎉 Perfect reconciliation — no issues found!")

    with tab3:
        ok = merged[merged['Audit_Status'] == 'Matched ✓']
        st.caption(f"{len(ok):,} matched records")
        st.dataframe(ok, use_container_width=True, height=430)

    with tab4:
        ms = merged[merged['Audit_Status'] == 'Missing in Source']
        mt = merged[merged['Audit_Status'] == 'Missing in Target']
        m1, m2 = st.columns(2)
        with m1:
            st.caption(f"Missing in Source — {len(ms)}")
            st.dataframe(ms, use_container_width=True, height=360) if len(ms) else st.success("None missing in source")
        with m2:
            st.caption(f"Missing in Target — {len(mt)}")
            st.dataframe(mt, use_container_width=True, height=360) if len(mt) else st.success("None missing in target")

    with tab5:
        a1, a2 = st.columns(2)
        with a1:
            st.markdown("**Status Distribution**")
            sc2 = merged['Audit_Status'].value_counts().reset_index()
            sc2.columns = ['Status', 'Count']
            st.dataframe(sc2, use_container_width=True)
        with a2:
            st.markdown("**Variance Statistics (non-zero)**")
            vd = merged[merged['Variance'] != 0][['Variance']].describe()
            st.dataframe(vd, use_container_width=True)
        st.markdown("**Top 10 Largest Variances**")
        tv = merged[merged['Audit_Status'] == 'Amount Discrepancy'].nlargest(10, 'Variance')
        if len(tv):
            st.dataframe(tv[[src_key, s_col, t_col, 'Variance', 'Variance_%']],
                         use_container_width=True)
        else:
            st.info("No amount discrepancies found.")

    # ── Export ─────────────────────────────────
    st.divider()
    st.markdown('<div class="section-title">📥 Export Report</div>', unsafe_allow_html=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    ex1, ex2 = st.columns(2)
    with ex1:
        st.download_button(
            label="⬇️  Download Excel Report (4 Sheets, Styled)",
            data=to_excel_bytes(merged, stats),
            file_name=f"audit_report_{ts}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    with ex2:
        st.download_button(
            label="⬇️  Download CSV (UTF-8 BOM, Excel-compatible)",
            data=merged.to_csv(index=False).encode('utf-8-sig'),
            file_name=f"audit_report_{ts}.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.markdown(f"""
    <div class="info-box gold" style="margin-top:1rem;">
        <p style="color:#8a96aa;margin:0;font-size:0.82rem;line-height:1.8;">
        📌 Excel report — <strong style="color:#c9a84c;">4 Colored Sheets:</strong>
        <code style="background:#1e2a42;padding:2px 5px;border-radius:3px;">Audit_Report</code>
        <code style="background:#1e2a42;padding:2px 5px;border-radius:3px;">Summary</code>
        <code style="background:#1e2a42;padding:2px 5px;border-radius:3px;">Issues_Only</code>
        <code style="background:#1e2a42;padding:2px 5px;border-radius:3px;">Matched_Only</code>
        </p>
    </div>
    """, unsafe_allow_html=True)
