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
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
#  Custom CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
    }

    /* Dark background */
    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
    }

    .main .block-container {
        padding: 2rem 2.5rem;
        max-width: 1400px;
    }

    /* Header */
    .audit-header {
        background: linear-gradient(135deg, #1c2b3a 0%, #0d1117 100%);
        border: 1px solid #21d9b0;
        border-radius: 12px;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    .audit-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(33,217,176,0.08) 0%, transparent 70%);
        border-radius: 50%;
    }
    .audit-header h1 {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 1.9rem;
        font-weight: 600;
        color: #21d9b0;
        margin: 0 0 0.4rem 0;
        letter-spacing: -0.5px;
    }
    .audit-header p {
        color: #8b949e;
        margin: 0;
        font-size: 0.95rem;
    }

    /* Section headers */
    .section-title {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #21d9b0;
        padding: 0.3rem 0;
        border-bottom: 1px solid #21272e;
        margin-bottom: 1rem;
    }

    /* Metric cards */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 0.75rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #161b22;
        border: 1px solid #21272e;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        transition: border-color 0.2s;
    }
    .metric-card:hover { border-color: #21d9b0; }
    .metric-card .label {
        font-size: 0.72rem;
        color: #8b949e;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 0.4rem;
    }
    .metric-card .value {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 1.7rem;
        font-weight: 600;
        color: #e6edf3;
        line-height: 1;
    }
    .metric-card .sub {
        font-size: 0.72rem;
        color: #8b949e;
        margin-top: 0.25rem;
    }
    .metric-card.green .value { color: #3fb950; }
    .metric-card.red .value { color: #f85149; }
    .metric-card.yellow .value { color: #e3b341; }
    .metric-card.blue .value { color: #58a6ff; }
    .metric-card.teal .value { color: #21d9b0; }

    /* Status badges */
    .badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.3px;
    }
    .badge-ok { background: #1a3a2a; color: #3fb950; border: 1px solid #2ea043; }
    .badge-miss-src { background: #3a2a1a; color: #e3b341; border: 1px solid #9e6a03; }
    .badge-miss-tgt { background: #2a1a3a; color: #bc8cff; border: 1px solid #6e40c9; }
    .badge-disc { background: #3a1a1a; color: #f85149; border: 1px solid #da3633; }
    .badge-dup { background: #1a2a3a; color: #58a6ff; border: 1px solid #1f6feb; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 1px solid #21272e;
    }
    [data-testid="stSidebar"] .stMarkdown p {
        color: #8b949e;
        font-size: 0.85rem;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #21d9b0, #1cb89a);
        color: #0d1117;
        border: none;
        border-radius: 8px;
        font-weight: 700;
        font-size: 0.9rem;
        padding: 0.6rem 1.8rem;
        letter-spacing: 0.3px;
        transition: all 0.2s;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 20px rgba(33,217,176,0.3);
    }

    /* Download button */
    .stDownloadButton > button {
        background: #161b22 !important;
        color: #21d9b0 !important;
        border: 1px solid #21d9b0 !important;
        border-radius: 8px;
        font-weight: 600;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: #161b22;
        border: 1px solid #21272e;
        border-radius: 8px;
        color: #e6edf3;
    }

    /* Dataframe */
    .stDataFrame { border: 1px solid #21272e; border-radius: 10px; overflow: hidden; }

    /* Selectbox */
    .stSelectbox > div > div {
        background: #161b22;
        border-color: #21272e;
        color: #e6edf3;
    }

    /* Alert boxes */
    .stSuccess { background: #1a3a2a; border-left-color: #3fb950; }
    .stInfo { background: #1a2a3a; border-left-color: #58a6ff; }
    .stWarning { background: #3a2a1a; border-left-color: #e3b341; }
    .stError { background: #3a1a1a; border-left-color: #f85149; }

    /* Info box */
    .info-box {
        background: #161b22;
        border: 1px solid #21272e;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .info-box.warning { border-left: 3px solid #e3b341; }
    .info-box.danger  { border-left: 3px solid #f85149; }
    .info-box.success { border-left: 3px solid #3fb950; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: #161b22;
        border-radius: 10px 10px 0 0;
        border-bottom: 2px solid #21272e;
        gap: 0;
    }
    .stTabs [data-baseweb="tab"] {
        color: #8b949e;
        font-weight: 600;
        font-size: 0.85rem;
        letter-spacing: 0.3px;
        padding: 0.7rem 1.5rem;
    }
    .stTabs [aria-selected="true"] {
        color: #21d9b0 !important;
        border-bottom: 2px solid #21d9b0 !important;
    }

    /* Divider */
    hr { border-color: #21272e; }

    /* Checkbox */
    .stCheckbox label span { color: #c9d1d9; font-size: 0.88rem; }

    /* Number input */
    .stNumberInput input {
        background: #161b22;
        border-color: #21272e;
        color: #e6edf3;
    }

    /* Multiselect */
    .stMultiSelect > div {
        background: #161b22;
        border-color: #21272e;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  Header
# ─────────────────────────────────────────────
st.markdown("""
<div class="audit-header">
    <h1>🔍 Myanmar Auditor Pro</h1>
    <p>Advanced Excel Reconciliation & Audit Tool — XLOOKUP Style Variance Detection</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  Helper Functions
# ─────────────────────────────────────────────

def load_excel(file, sheet_name=0, header_row=0, skip_rows=0):
    """Load Excel with configurable options."""
    try:
        df = pd.read_excel(
            file,
            sheet_name=sheet_name,
            header=header_row if header_row >= 0 else None,
            skiprows=skip_rows if skip_rows > 0 else None
        )
        # Clean column names
        df.columns = [str(c).strip() for c in df.columns]
        return df, None
    except Exception as e:
        return None, str(e)


def detect_duplicates(df, key_col):
    """Return duplicate rows by key column."""
    return df[df.duplicated(subset=[key_col], keep=False)].copy()


def compute_summary(df_result, amt_src, amt_tgt):
    """Compute audit summary statistics."""
    total = len(df_result)
    matched = (df_result['Audit_Status'] == 'Matched ✓').sum()
    miss_src = (df_result['Audit_Status'] == 'Missing in Source').sum()
    miss_tgt = (df_result['Audit_Status'] == 'Missing in Target').sum()
    discrepancy = (df_result['Audit_Status'] == 'Amount Discrepancy').sum()

    src_total = df_result[amt_src].fillna(0).sum()
    tgt_total = df_result[amt_tgt].fillna(0).sum()
    total_variance = df_result['Variance'].sum()
    pct_matched = (matched / total * 100) if total > 0 else 0

    return {
        'total': total,
        'matched': matched,
        'miss_src': miss_src,
        'miss_tgt': miss_tgt,
        'discrepancy': discrepancy,
        'src_total': src_total,
        'tgt_total': tgt_total,
        'total_variance': total_variance,
        'pct_matched': pct_matched
    }


def get_status(row, src_col, tgt_col, tolerance):
    if pd.isna(row[src_col]): return 'Missing in Source'
    if pd.isna(row[tgt_col]): return 'Missing in Target'
    if abs(row['Variance']) > tolerance: return 'Amount Discrepancy'
    return 'Matched ✓'


def style_status(val):
    colors = {
        'Matched ✓':         'background-color:#1a3a2a;color:#3fb950',
        'Missing in Source': 'background-color:#3a2a1a;color:#e3b341',
        'Missing in Target': 'background-color:#2a1a3a;color:#bc8cff',
        'Amount Discrepancy':'background-color:#3a1a1a;color:#f85149',
    }
    return colors.get(val, '')


def style_variance(val):
    try:
        v = float(val)
        if v > 0:   return 'color:#f85149'
        if v < 0:   return 'color:#e3b341'
        return 'color:#3fb950'
    except:
        return ''


def to_excel_bytes(df_main, df_summary_data, summary_stats):
    """Export multi-sheet Excel report."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        wb = writer.book

        # ── Formats ──────────────────────────────
        hdr_fmt = wb.add_format({
            'bold': True, 'bg_color': '#1c2b3a', 'font_color': '#21d9b0',
            'border': 1, 'border_color': '#21272e', 'font_name': 'Calibri'
        })
        ok_fmt   = wb.add_format({'bg_color': '#1a3a2a', 'font_color': '#3fb950'})
        miss_fmt = wb.add_format({'bg_color': '#3a2a1a', 'font_color': '#e3b341'})
        mitp_fmt = wb.add_format({'bg_color': '#2a1a3a', 'font_color': '#bc8cff'})
        disc_fmt = wb.add_format({'bg_color': '#3a1a1a', 'font_color': '#f85149'})
        num_fmt  = wb.add_format({'num_format': '#,##0.00'})
        pct_fmt  = wb.add_format({'num_format': '0.00%'})
        title_fmt = wb.add_format({
            'bold': True, 'font_size': 14, 'font_color': '#21d9b0',
            'font_name': 'Calibri'
        })

        # ── Sheet 1: Full Audit Report ────────────
        df_main.to_excel(writer, index=False, sheet_name='Audit_Report', startrow=2)
        ws = writer.sheets['Audit_Report']
        ws.write(0, 0, f'Myanmar Auditor Pro — Generated {datetime.now().strftime("%Y-%m-%d %H:%M")}', title_fmt)

        for col_num, col_name in enumerate(df_main.columns):
            ws.write(2, col_num, col_name, hdr_fmt)
            col_width = max(len(str(col_name)) + 4, 14)
            ws.set_column(col_num, col_num, col_width)

        status_col = df_main.columns.get_loc('Audit_Status')
        for row_num, status in enumerate(df_main['Audit_Status'], start=3):
            fmt = {'Matched ✓': ok_fmt, 'Missing in Source': miss_fmt,
                   'Missing in Target': mitp_fmt, 'Amount Discrepancy': disc_fmt}.get(status)
            if fmt:
                ws.write(row_num, status_col, status, fmt)

        ws.freeze_panes(3, 0)
        ws.autofilter(2, 0, 2 + len(df_main), len(df_main.columns) - 1)

        # ── Sheet 2: Summary ─────────────────────
        ws2 = wb.add_worksheet('Summary')
        ws2.write(0, 0, 'Audit Summary', title_fmt)
        ws2.set_column(0, 0, 30)
        ws2.set_column(1, 1, 20)

        rows = [
            ('Report Date', datetime.now().strftime('%Y-%m-%d %H:%M')),
            ('Total Records', summary_stats['total']),
            ('Matched ✓', summary_stats['matched']),
            ('Missing in Source', summary_stats['miss_src']),
            ('Missing in Target', summary_stats['miss_tgt']),
            ('Amount Discrepancy', summary_stats['discrepancy']),
            ('Match Rate (%)', f"{summary_stats['pct_matched']:.2f}%"),
            ('Source Total', summary_stats['src_total']),
            ('Target Total', summary_stats['tgt_total']),
            ('Net Variance', summary_stats['total_variance']),
        ]
        for i, (k, v) in enumerate(rows, start=2):
            ws2.write(i, 0, k, hdr_fmt)
            ws2.write(i, 1, v)

        # ── Sheet 3: Discrepancies Only ───────────
        df_issues = df_main[df_main['Audit_Status'] != 'Matched ✓'].copy()
        df_issues.to_excel(writer, index=False, sheet_name='Issues_Only', startrow=1)
        ws3 = writer.sheets['Issues_Only']
        ws3.write(0, 0, f'Issues Only — {len(df_issues)} records', title_fmt)
        for col_num, col_name in enumerate(df_issues.columns):
            ws3.write(1, col_num, col_name, hdr_fmt)
            ws3.set_column(col_num, col_num, max(len(str(col_name)) + 4, 14))

    return output.getvalue()


# ─────────────────────────────────────────────
#  Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-title">📁 File Upload</div>', unsafe_allow_html=True)
    source_file = st.file_uploader(
        "Source File (Cash Book / GL)",
        type=['xlsx', 'xls'],
        help="စစ်ဆေးမည့် ဖိုင်"
    )
    target_file = st.file_uploader(
        "Target File (Bank Statement / Master)",
        type=['xlsx', 'xls'],
        help="အတည်ပြုမည့် ဖိုင်"
    )

    st.markdown('<div class="section-title">⚙️ Advanced Options</div>', unsafe_allow_html=True)

    with st.expander("Source File Settings", expanded=False):
        src_sheet     = st.number_input("Sheet Index (0-based)", min_value=0, value=0, key='src_sheet')
        src_header    = st.number_input("Header Row", min_value=0, value=0, key='src_header')
        src_skip      = st.number_input("Skip Rows", min_value=0, value=0, key='src_skip')

    with st.expander("Target File Settings", expanded=False):
        tgt_sheet     = st.number_input("Sheet Index (0-based)", min_value=0, value=0, key='tgt_sheet')
        tgt_header    = st.number_input("Header Row", min_value=0, value=0, key='tgt_header')
        tgt_skip      = st.number_input("Skip Rows", min_value=0, value=0, key='tgt_skip')

    with st.expander("Audit Rules", expanded=False):
        tolerance     = st.number_input("Variance Tolerance (±)", min_value=0.0, value=0.0, step=0.01,
                                        help="0 means exact match required")
        case_sens     = st.checkbox("Case-sensitive Key Matching", value=False)
        strip_spaces  = st.checkbox("Strip Whitespace from Keys", value=True)
        flag_dups     = st.checkbox("Flag Duplicate Keys", value=True)

    st.markdown("---")
    st.markdown('<p style="color:#8b949e;font-size:0.78rem;">Myanmar Auditor Pro v2.0<br>Built with Streamlit + Pandas</p>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  Main Content
# ─────────────────────────────────────────────
if not (source_file and target_file):
    st.markdown("""
    <div class="info-box success">
        <h4 style="color:#3fb950;margin:0 0 0.5rem 0;">🚀 Getting Started</h4>
        <p style="color:#8b949e;margin:0;">
            Sidebar မှာ Excel ဖိုင် ၂ ခု Upload လုပ်ပါ — Source (Cash Book/GL) နှင့် Target (Bank/Master).
            <br><br>
            <strong style="color:#c9d1d9;">Features:</strong> Multi-sheet support · Duplicate detection · Variance tolerance ·
            3-sheet Excel export · Summary analytics · Filtered views
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Load Files ────────────────────────────────
df_src, err_src = load_excel(source_file, src_sheet, src_header, src_skip)
df_tgt, err_tgt = load_excel(target_file, tgt_sheet, tgt_header, tgt_skip)

if err_src:
    st.error(f"Source file error: {err_src}")
    st.stop()
if err_tgt:
    st.error(f"Target file error: {err_tgt}")
    st.stop()

# ── Preview ───────────────────────────────────
st.markdown('<div class="section-title">📋 Data Preview</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    st.caption(f"**Source** — {len(df_src):,} rows × {len(df_src.columns)} cols")
    st.dataframe(df_src.head(8), use_container_width=True, height=240)
with col2:
    st.caption(f"**Target** — {len(df_tgt):,} rows × {len(df_tgt.columns)} cols")
    st.dataframe(df_tgt.head(8), use_container_width=True, height=240)

st.divider()

# ── Audit Configuration ───────────────────────
st.markdown('<div class="section-title">🛠 Audit Configuration</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    src_key = st.selectbox("Source Key Column", options=df_src.columns,
                           help="တိုက်စစ်မည့် ID / Voucher No (Source)")
with c2:
    tgt_key = st.selectbox("Target Key Column", options=df_tgt.columns,
                           help="တိုက်စစ်မည့် ID / Voucher No (Target)")
with c3:
    src_amt = st.selectbox("Source Amount Column", options=df_src.columns)
with c4:
    tgt_amt = st.selectbox("Target Amount Column", options=df_tgt.columns)

extra_src_cols = st.multiselect(
    "Additional Source Columns to include in report",
    options=[c for c in df_src.columns if c not in [src_key, src_amt]],
    default=[]
)
extra_tgt_cols = st.multiselect(
    "Additional Target Columns to include in report",
    options=[c for c in df_tgt.columns if c not in [tgt_key, tgt_amt]],
    default=[]
)

st.markdown("")
run_btn = st.button("▶  Run Full Audit Process", use_container_width=False)

# ─────────────────────────────────────────────
#  Run Audit
# ─────────────────────────────────────────────
if run_btn:
    with st.spinner("Auditing…"):

        # Prepare working copies
        src = df_src[[src_key, src_amt] + extra_src_cols].copy()
        tgt = df_tgt[[tgt_key, tgt_amt] + extra_tgt_cols].copy()

        # Key preprocessing
        if strip_spaces:
            src[src_key] = src[src_key].astype(str).str.strip()
            tgt[tgt_key] = tgt[tgt_key].astype(str).str.strip()
        if not case_sens:
            src[src_key] = src[src_key].astype(str).str.upper()
            tgt[tgt_key] = tgt[tgt_key].astype(str).str.upper()

        # Duplicate detection
        dup_src = detect_duplicates(src, src_key) if flag_dups else pd.DataFrame()
        dup_tgt = detect_duplicates(tgt, tgt_key) if flag_dups else pd.DataFrame()

        # Outer merge
        src_renamed = src.rename(columns={src_key: '_KEY_', src_amt: src_amt + '_Source'})
        tgt_renamed = tgt.rename(columns={tgt_key: '_KEY_', tgt_amt: tgt_amt + '_Target'})

        for c in extra_src_cols:
            src_renamed = src_renamed.rename(columns={c: c + '_Source'})
        for c in extra_tgt_cols:
            tgt_renamed = tgt_renamed.rename(columns={c: c + '_Target'})

        merged = pd.merge(src_renamed, tgt_renamed, on='_KEY_', how='outer')
        merged.rename(columns={'_KEY_': src_key}, inplace=True)

        # Variance & Status
        s_col = src_amt + '_Source'
        t_col = tgt_amt + '_Target'
        merged['Variance'] = merged[s_col].fillna(0) - merged[t_col].fillna(0)
        merged['Variance_%'] = merged.apply(
            lambda r: (r['Variance'] / r[t_col] * 100) if (pd.notna(r[t_col]) and r[t_col] != 0) else np.nan,
            axis=1
        )
        merged['Audit_Status'] = merged.apply(lambda r: get_status(r, s_col, t_col, tolerance), axis=1)

        # Summary stats
        stats = compute_summary(merged, s_col, t_col)

    # ── Results ───────────────────────────────
    st.success(f"✅ Audit Complete — {stats['total']:,} records processed in {datetime.now().strftime('%H:%M:%S')}")

    # Metrics
    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-card teal">
            <div class="label">Total Records</div>
            <div class="value">{stats['total']:,}</div>
            <div class="sub">after merge</div>
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
        <div class="metric-card yellow">
            <div class="label">Missing Items</div>
            <div class="value">{stats['miss_src'] + stats['miss_tgt']:,}</div>
            <div class="sub">src: {stats['miss_src']} / tgt: {stats['miss_tgt']}</div>
        </div>
        <div class="metric-card blue">
            <div class="label">Net Variance</div>
            <div class="value">{stats['total_variance']:,.0f}</div>
            <div class="sub">src−tgt total</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Duplicate warnings ─────────────────────
    if flag_dups and (len(dup_src) > 0 or len(dup_tgt) > 0):
        with st.expander(f"⚠️ Duplicate Keys Detected — Source: {len(dup_src)} rows, Target: {len(dup_tgt)} rows"):
            dc1, dc2 = st.columns(2)
            with dc1:
                st.caption("Source Duplicates")
                if len(dup_src): st.dataframe(dup_src, use_container_width=True)
                else: st.info("No duplicates")
            with dc2:
                st.caption("Target Duplicates")
                if len(dup_tgt): st.dataframe(dup_tgt, use_container_width=True)
                else: st.info("No duplicates")

    # ── Tabs ──────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Full Report",
        "❌ Issues Only",
        "✅ Matched",
        "🔍 Missing",
        "📈 Analytics"
    ])

    with tab1:
        st.caption(f"All {len(merged):,} records")
        st.dataframe(
            merged.style
                .applymap(style_status, subset=['Audit_Status'])
                .applymap(style_variance, subset=['Variance']),
            use_container_width=True,
            height=450
        )

    with tab2:
        issues = merged[merged['Audit_Status'] != 'Matched ✓']
        st.caption(f"{len(issues):,} issues found")
        if len(issues):
            st.dataframe(
                issues.style.applymap(style_status, subset=['Audit_Status']),
                use_container_width=True, height=420
            )
        else:
            st.success("🎉 No issues found! All records matched.")

    with tab3:
        ok = merged[merged['Audit_Status'] == 'Matched ✓']
        st.caption(f"{len(ok):,} matched records")
        st.dataframe(ok, use_container_width=True, height=420)

    with tab4:
        miss_src_df = merged[merged['Audit_Status'] == 'Missing in Source']
        miss_tgt_df = merged[merged['Audit_Status'] == 'Missing in Target']
        mc1, mc2 = st.columns(2)
        with mc1:
            st.caption(f"Missing in Source — {len(miss_src_df)} records")
            if len(miss_src_df):
                st.dataframe(miss_src_df, use_container_width=True, height=350)
            else:
                st.success("None missing in source")
        with mc2:
            st.caption(f"Missing in Target — {len(miss_tgt_df)} records")
            if len(miss_tgt_df):
                st.dataframe(miss_tgt_df, use_container_width=True, height=350)
            else:
                st.success("None missing in target")

    with tab5:
        st.markdown("**Status Distribution**")
        status_counts = merged['Audit_Status'].value_counts()
        ac1, ac2 = st.columns(2)
        with ac1:
            st.dataframe(
                status_counts.reset_index().rename(columns={'index': 'Status', 'Audit_Status': 'Count'}),
                use_container_width=True
            )
        with ac2:
            # Variance distribution stats
            var_df = merged[merged['Variance'] != 0][['Variance']].describe()
            st.caption("Variance Statistics (non-zero)")
            st.dataframe(var_df, use_container_width=True)

        st.markdown("**Top Variances**")
        top_var = merged[merged['Audit_Status'] == 'Amount Discrepancy'].nlargest(10, 'Variance')
        if len(top_var):
            st.dataframe(
                top_var[[src_key, s_col, t_col, 'Variance', 'Variance_%']],
                use_container_width=True
            )
        else:
            st.info("No amount discrepancies found.")

    # ── Export ─────────────────────────────────
    st.divider()
    st.markdown('<div class="section-title">📥 Export Report</div>', unsafe_allow_html=True)
    ex1, ex2 = st.columns(2)

    with ex1:
        excel_bytes = to_excel_bytes(merged, None, stats)
        fname = f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        st.download_button(
            label="⬇️  Download Excel Report (3 Sheets)",
            data=excel_bytes,
            file_name=fname,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    with ex2:
        csv_bytes = merged.to_csv(index=False).encode('utf-8-sig')
        csv_fname = f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        st.download_button(
            label="⬇️  Download CSV (UTF-8 BOM)",
            data=csv_bytes,
            file_name=csv_fname,
            mime="text/csv",
            use_container_width=True
        )

    st.markdown(f"""
    <div class="info-box" style="margin-top:1rem">
        <p style="color:#8b949e;margin:0;font-size:0.82rem;">
        📌 Excel report contains 3 sheets: <strong style="color:#c9d1d9">Audit_Report</strong> (full data with conditional formatting) ·
        <strong style="color:#c9d1d9">Summary</strong> (key statistics) ·
        <strong style="color:#c9d1d9">Issues_Only</strong> (filtered discrepancies only)
        </p>
    </div>
    """, unsafe_allow_html=True)
