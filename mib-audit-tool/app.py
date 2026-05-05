import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime
import warnings

# Library engines check
try:
    import openpyxl
except ImportError:
    st.error("Missing 'openpyxl' library. Please add it to requirements.txt")

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
#  Custom CSS — Dark Premium Theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0;
    }

    /* ── Header ── */
    .header-container {
        background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%);
        padding: 2rem;
        border-radius: 15px;
        border-left: 5px solid #fbbf24;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    }
    
    .header-container h1 {
        color: #fbbf24;
        font-weight: 700;
        margin: 0;
    }

    /* ── Metric Cards ── */
    .metric-card {
        background: #1e293b;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #334155;
        text-align: center;
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: #fbbf24;
    }
    .metric-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2rem;
        font-weight: 700;
        color: #fbbf24;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* ── Styled Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #1e293b;
        border-radius: 8px 8px 0 0;
        color: #94a3b8;
        padding: 0 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #fbbf24 !important;
        color: #0f172a !important;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #334155;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  Header Section
# ─────────────────────────────────────────────
st.markdown("""
<div class="header-container">
    <h1>📊 Myanmar Auditor Pro <span style='font-size:0.8rem; vertical-align:middle; color:#94a3b8;'>v3.0</span></h1>
    <p style='color:#94a3b8; margin-top:0.5rem;'>Professional Excel Reconciliation & Smart Audit Variance Detection</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  Helper Functions (Core Logic)
# ─────────────────────────────────────────────

def load_data(file, sheet=0):
    if file is None: return None
    try:
        if file.name.endswith('.csv'):
            return pd.read_csv(file)
        # Try different engines for Excel
        for engine in ['openpyxl', 'xlrd']:
            try:
                return pd.read_excel(file, sheet_name=sheet, engine=engine)
            except:
                continue
        return None
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

# ─────────────────────────────────────────────
#  Sidebar Configuration
# ─────────────────────────────────────────────
with st.sidebar:
    st.title("📁 Data Source")
    src_file = st.file_uploader("Source (Cash Book/GL)", type=['xlsx', 'xls', 'csv'])
    tgt_file = st.file_uploader("Target (Bank/Statement)", type=['xlsx', 'xls', 'csv'])
    
    st.divider()
    st.title("⚙️ Audit Rules")
    tolerance = st.number_input("Variance Tolerance (±)", min_value=0.0, value=0.0)
    strip_ws = st.checkbox("Strip Spaces", value=True)
    
    st.info("💡 Hint: Use unique IDs like Voucher No or Transaction ID as Keys.")

# ─────────────────────────────────────────────
#  Main Execution Logic
# ─────────────────────────────────────────────
if src_file and tgt_file:
    df_src = load_data(src_file)
    df_tgt = load_data(tgt_file)
    
    if df_src is not None and df_tgt is not None:
        st.markdown("### 🛠 Step 1: Map your columns")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1: src_key = st.selectbox("Source Key", df_src.columns)
        with col2: tgt_key = st.selectbox("Target Key", df_tgt.columns)
        with col3: src_amt = st.selectbox("Source Amount", df_src.columns)
        with col4: tgt_amt = st.selectbox("Target Amount", df_tgt.columns)
        
        if st.button("🚀 Run Audit Process", use_container_width=True):
            # 1. Processing
            s = df_src.copy()
            t = df_tgt.copy()
            
            if strip_ws:
                s[src_key] = s[src_key].astype(str).str.strip()
                t[tgt_key] = t[tgt_key].astype(str).str.strip()

            # 2. XLOOKUP / Merge Logic
            merged = pd.merge(
                s, t, left_on=src_key, right_on=tgt_key, 
                how='outer', suffixes=('_Src', '_Tgt')
            )
            
            # 3. Calculations
            merged['Variance'] = merged[src_amt].fillna(0) - merged[tgt_amt].fillna(0)
            
            def check_status(r):
                if pd.isna(r[src_amt]): return "Missing in Source"
                if pd.isna(r[tgt_amt]): return "Missing in Target"
                if abs(r['Variance']) > tolerance: return "Discrepancy"
                return "Matched ✓"
            
            merged['Audit_Status'] = merged.apply(check_status, axis=1)
            
            # ─────────────────────────────────────────────
            #  Dashboard Stats
            # ─────────────────────────────────────────────
            st.divider()
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.markdown(f'<div class="metric-card"><div class="metric-label">Matched</div><div class="metric-value" style="color:#10b981;">{(merged["Audit_Status"]=="Matched ✓").sum()}</div></div>', unsafe_allow_html=True)
            with m2:
                st.markdown(f'<div class="metric-card"><div class="metric-label">Discrepancy</div><div class="metric-value" style="color:#ef4444;">{(merged["Audit_Status"]=="Discrepancy").sum()}</div></div>', unsafe_allow_html=True)
            with m3:
                st.markdown(f'<div class="metric-card"><div class="metric-label">Missing</div><div class="metric-value" style="color:#f59e0b;">{(merged["Audit_Status"].str.contains("Missing")).sum()}</div></div>', unsafe_allow_html=True)
            with m4:
                st.markdown(f'<div class="metric-card"><div class="metric-label">Net Variance</div><div class="metric-value">{merged["Variance"].sum():,.0f}</div></div>', unsafe_allow_html=True)

            # ─────────────────────────────────────────────
            #  Results Display
            # ─────────────────────────────────────────────
            t1, t2 = st.tabs(["📊 Full Report", "🔍 Issues Only"])
            with t1:
                st.dataframe(merged, use_container_width=True)
            with t2:
                st.dataframe(merged[merged['Audit_Status'] != "Matched ✓"], use_container_width=True)
            
            # Export
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                merged.to_excel(writer, index=False, sheet_name='Audit_Report')
            
            st.download_button(
                label="📥 Download Professional Audit Report",
                data=output.getvalue(),
                file_name=f"Audit_Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

else:
    st.markdown("""
    <div style="text-align:center; padding: 5rem; border: 2px dashed #334155; border-radius: 20px;">
        <h2 style="color:#64748b;">Waiting for data...</h2>
        <p style="color:#475569;">Please upload your Source and Target files in the sidebar to begin.</p>
    </div>
    """, unsafe_allow_html=True)
