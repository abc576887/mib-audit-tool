import streamlit as st
import pandas as pd
import io
from datetime import datetime

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SGF Audit Workflow Tool",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Global Styles ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Pyidaungsu&display=swap');

html, body, [class*="css"] {
    font-family: 'Pyidaungsu', 'Segoe UI', sans-serif;
}

/* Header */
.main-header {
    background: linear-gradient(135deg, #1a237e 0%, #283593 60%, #3949ab 100%);
    color: white;
    padding: 28px 32px;
    border-radius: 12px;
    margin-bottom: 28px;
    display: flex;
    align-items: center;
    gap: 16px;
    box-shadow: 0 4px 20px rgba(26,35,126,0.25);
}
.main-header h1 { margin: 0; font-size: 1.75rem; letter-spacing: 0.3px; }
.main-header p  { margin: 4px 0 0; font-size: 0.88rem; opacity: 0.85; }

/* Step Card */
.step-card {
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 22px 24px;
    margin-bottom: 24px;
    background: #ffffff;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.step-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #1a237e;
    color: white;
    font-size: 0.78rem;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 20px;
    letter-spacing: 0.5px;
    margin-bottom: 10px;
}
.step-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #1a237e;
    margin: 0 0 16px;
}

/* KPI Cards */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
    margin-bottom: 20px;
}
.kpi-card {
    border-radius: 10px;
    padding: 18px 20px;
    text-align: center;
    font-size: 0.82rem;
    font-weight: 600;
    letter-spacing: 0.2px;
}
.kpi-card .kpi-num {
    font-size: 2rem;
    font-weight: 800;
    display: block;
    margin-bottom: 4px;
}
.kpi-green  { background: #e8f5e9; color: #2e7d32; border: 1px solid #a5d6a7; }
.kpi-red    { background: #ffebee; color: #c62828; border: 1px solid #ef9a9a; }
.kpi-orange { background: #fff3e0; color: #e65100; border: 1px solid #ffcc80; }

/* Step connector line */
.step-divider {
    display: flex;
    align-items: center;
    margin: 4px 0 20px;
    gap: 12px;
    color: #9e9e9e;
    font-size: 0.8rem;
}
.step-divider::before,
.step-divider::after {
    content: '';
    flex: 1;
    border-top: 1px dashed #bdbdbd;
}

/* Buttons */
div[data-testid="stButton"] > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    letter-spacing: 0.3px !important;
    transition: all 0.2s !important;
}
div[data-testid="stButton"] > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
}

/* Dataframe */
div[data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }

/* Info / Success / Warning tweaks */
div[data-testid="stAlert"] { border-radius: 8px !important; }

/* Tab styling */
button[data-baseweb="tab"] { font-size: 0.88rem !important; font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <div>
        <h1>🛡️ SGF Raw Data Audit Workflow</h1>
        <p>Reconciliation & Discrepancy Detection System &nbsp;|&nbsp; SGF ရေးမှတ်ချက် စစ်ဆေးရေးစနစ်</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Session State Init ───────────────────────────────────────────────────────
for key in ("working_df", "header_row"):
    if key not in st.session_state:
        st.session_state[key] = None if key == "working_df" else 1


# ════════════════════════════════════════════════════════════════════════════════
# STEP 1 — Working Paper
# ════════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="step-badge">STEP 1</div>', unsafe_allow_html=True)
st.markdown('<div class="step-title">📂 Create Working Paper (Source File)</div>', unsafe_allow_html=True)

with st.container():
    file_1 = st.file_uploader(
        "SGF Raw File တင်ပါ (ဥပမာ — SGF Raw (1-2025).xlsx)",
        type=["xlsx", "xls", "xlsb"],
        key="uploader_source",
    )

    if file_1:
        try:
            xl1 = pd.ExcelFile(file_1)
        except Exception as e:
            st.error(f"❌ File ဖတ်မရပါ: {e}")
            st.stop()

        c1, c2 = st.columns([2, 1])
        with c1:
            sheet_name = st.selectbox(
                "Sheet ရွေးပါ",
                xl1.sheet_names,
                help="Working Paper ဆွဲမည့် Sheet ကိုရွေးပါ",
            )
        with c2:
            header_row = st.number_input(
                "Header Row (1-indexed)",
                min_value=1,
                max_value=20,
                value=1,
                help="ပထမဆုံး Row ကို 1 ဟုသတ်မှတ်ပါ",
            )
            st.session_state.header_row = header_row

        try:
            # pandas header is 0-indexed; user inputs 1-indexed
            df1_raw = pd.read_excel(
                file_1, sheet_name=sheet_name, header=int(header_row) - 1
            )
        except Exception as e:
            st.error(f"❌ Sheet ဖတ်မရပါ: {e}")
            st.stop()

        with st.expander("📋 Source Data Preview (first 5 rows)", expanded=True):
            st.dataframe(df1_raw.head(5), use_container_width=True)

        selected_cols = st.multiselect(
            "Working Paper အတွက် Column များရွေးပါ",
            df1_raw.columns.tolist(),
            default=df1_raw.columns.tolist(),
            help="လိုအပ်သော Column များကိုသာ ရွေးပါ",
        )

        if selected_cols:
            working_df = df1_raw[selected_cols].copy()

            col_a, col_b = st.columns(2)
            with col_a:
                remove_empty = st.checkbox("Empty Rows ဖယ်ထုတ်မည်", value=True)
            with col_b:
                remove_dupes = st.checkbox("Duplicate Rows ဖယ်ထုတ်မည်", value=False)

            if remove_empty:
                before = len(working_df)
                working_df.dropna(how="all", inplace=True)
                removed = before - len(working_df)
                if removed:
                    st.info(f"ℹ️ Empty Rows {removed} ကြောင်း ဖယ်ထုတ်လိုက်သည်")

            if remove_dupes:
                before = len(working_df)
                working_df.drop_duplicates(inplace=True)
                removed = before - len(working_df)
                if removed:
                    st.info(f"ℹ️ Duplicate Rows {removed} ကြောင်း ဖယ်ထုတ်လိုက်သည်")

            st.session_state.working_df = working_df
            st.success(
                f"✅ Working Paper အဆင်သင့် — {len(working_df):,} records, "
                f"{len(selected_cols)} columns"
            )
        else:
            st.warning("⚠️ အနည်းဆုံး Column တစ်ခုရွေးပေးပါ")
            st.session_state.working_df = None

    else:
        st.session_state.working_df = None

# ════════════════════════════════════════════════════════════════════════════════
# STEP 2 — Reconciliation
# ════════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="step-divider">↓ Step 1 ပြီးမှ Step 2 ဆက်လုပ်ပါ ↓</div>', unsafe_allow_html=True)

working_df = st.session_state.working_df
header_row  = st.session_state.header_row or 1

st.markdown('<div class="step-badge">STEP 2</div>', unsafe_allow_html=True)
st.markdown('<div class="step-title">🔍 Reconciliation — တိုက်စစ်ခြင်း</div>', unsafe_allow_html=True)

if working_df is None:
    st.info("📌 Step 1 တွင် Source File ကို အရင်တင်ပြီး Working Paper ပြင်ဆင်ပေးပါ")
    st.stop()

file_2 = st.file_uploader(
    "Target File တင်ပါ (တိုက်စစ်မည့် ဖိုင်)",
    type=["xlsx", "xls", "xlsb"],
    key="uploader_target",
)

if file_2:
    try:
        xl2 = pd.ExcelFile(file_2)
    except Exception as e:
        st.error(f"❌ Target File ဖတ်မရပါ: {e}")
        st.stop()

    sheet_name_2 = st.selectbox(
        "Target Sheet ရွေးပါ",
        xl2.sheet_names,
        help="တိုက်စစ်မည့် Sheet ကိုရွေးပါ",
    )

    try:
        df2 = pd.read_excel(
            file_2, sheet_name=sheet_name_2, header=int(header_row) - 1
        )
    except Exception as e:
        st.error(f"❌ Target Sheet ဖတ်မရပါ: {e}")
        st.stop()

    with st.expander("📋 Target Data Preview (first 5 rows)"):
        st.dataframe(df2.head(5), use_container_width=True)

    st.markdown("**🔑 Key Column ချိတ်ဆက်ခြင်း (Join Key)**")
    c1, c2 = st.columns(2)
    with c1:
        key_src = st.selectbox("Source (Working Paper) Key", working_df.columns, key="key_src")
    with c2:
        key_tgt = st.selectbox("Target File Key", df2.columns, key="key_tgt")

    st.markdown("---")

    if st.button("🚀 Reconciliation စတင်မည်", use_container_width=True, type="primary"):

        with st.spinner("စစ်ဆေးနေသည်..."):
            src_keys = working_df[key_src].astype(str).str.strip()
            tgt_keys = df2[key_tgt].astype(str).str.strip()

            missing_in_target = working_df[~src_keys.isin(tgt_keys)].copy()
            missing_in_source = df2[~tgt_keys.isin(src_keys)].copy()

            matched_count = src_keys.isin(tgt_keys).sum()

            # ── Safe Merge (Column name ထပ်နေမှု ကာကွယ်ခြင်း) ──────────────
            # ပြဿနာ: Source နဲ့ Target မှာ Column name တူနေရင်
            #         rename လုပ်လိုက်တဲ့အခါ column နှစ်ခုထပ်နေပြီး
            #         pandas က merge မလုပ်နိုင်ဘဲ ValueError ပေးသည်။
            # အဖြေ:  merge မလုပ်မီ unique join key column တစ်ခုထည့်ပြီး
            #         merge key ကို တိတိကျကျ သတ်မှတ်ပေးသည်။

            JOIN_KEY = "__merge_key__"   # temporary unique join column

            src_temp = working_df.copy()
            src_temp[JOIN_KEY] = src_temp[key_src].astype(str).str.strip()

            tgt_temp = df2.copy()
            tgt_temp[JOIN_KEY] = tgt_temp[key_tgt].astype(str).str.strip()

            # Source နဲ့ Target မှာ Column name တူနေလျှင် suffix ချပေးသည်
            src_cols = set(src_temp.columns) - {JOIN_KEY}
            tgt_cols = set(tgt_temp.columns) - {JOIN_KEY}
            overlap  = src_cols & tgt_cols

            if overlap:
                src_temp = src_temp.rename(
                    columns={c: f"{c}_Source" for c in overlap}
                )
                tgt_temp = tgt_temp.rename(
                    columns={c: f"{c}_Target" for c in overlap}
                )

            comparison_df = pd.merge(
                src_temp, tgt_temp,
                on=JOIN_KEY,
                how="inner",
            )
            # temporary key ဖယ်ထုတ်ပြီး ရှင်းသပ်သော output ပေးသည်
            comparison_df.drop(columns=[JOIN_KEY], inplace=True)
            src_temp.drop(columns=[JOIN_KEY], inplace=True)
            tgt_temp.drop(columns=[JOIN_KEY], inplace=True)

        # ── KPI Summary ────────────────────────────────────────────────────
        st.markdown(f"""
        <div class="kpi-grid">
            <div class="kpi-card kpi-green">
                <span class="kpi-num">{matched_count:,}</span>
                ✅ Matched Records
            </div>
            <div class="kpi-card kpi-red">
                <span class="kpi-num">{len(missing_in_target):,}</span>
                ❌ Target မှာ မပါတာ
            </div>
            <div class="kpi-card kpi-orange">
                <span class="kpi-num">{len(missing_in_source):,}</span>
                ⚠️ Source မှာ မပါတာ
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Tabs ───────────────────────────────────────────────────────────
        tab1, tab2, tab3 = st.tabs([
            f"❌ Target မှာ မပါတာ ({len(missing_in_target)})",
            f"⚠️ Source မှာ မပါတာ ({len(missing_in_source)})",
            f"🔗 Matched Comparison ({len(comparison_df)})",
        ])

        with tab1:
            if missing_in_target.empty:
                st.success("🎉 Target ဖိုင်ထဲတွင် Source ရှိသမျှ records အားလုံးတွေ့ပါသည်")
            else:
                st.error(f"Source တွင်ရှိပြီး Target တွင် မတွေ့ရသည့် records {len(missing_in_target):,} ခု")
                st.dataframe(missing_in_target, use_container_width=True, height=280)

        with tab2:
            if missing_in_source.empty:
                st.success("🎉 Target records အားလုံးကို Source တွင်တွေ့ပါသည်")
            else:
                st.warning(f"Target တွင်ရှိပြီး Source Working Paper တွင် မပါသည့် records {len(missing_in_source):,} ခု")
                st.dataframe(missing_in_source, use_container_width=True, height=280)

        with tab3:
            st.info(f"နှစ်ဖိုင်လုံးတွင် ကိုက်ညီသည့် records {len(comparison_df):,} ခု (Source & Target columns တွဲပြထားသည်)")
            st.dataframe(comparison_df, use_container_width=True, height=280)

        # ── Excel Export ───────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("**📥 Audit Report Export**")

        output = io.BytesIO()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")

        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            workbook = writer.book

            # Formats
            hdr_fmt = workbook.add_format({
                "bold": True, "bg_color": "#1a237e", "font_color": "white",
                "border": 1, "align": "center", "valign": "vcenter",
            })
            red_fmt   = workbook.add_format({"bg_color": "#FFEBEE", "border": 1})
            orange_fmt= workbook.add_format({"bg_color": "#FFF3E0", "border": 1})
            green_fmt = workbook.add_format({"bg_color": "#E8F5E9", "border": 1})

            def write_sheet(df, sheet, cell_fmt):
                df.to_excel(writer, sheet_name=sheet, index=False, startrow=1, header=False)
                ws = writer.sheets[sheet]
                for col_num, val in enumerate(df.columns):
                    ws.write(0, col_num, val, hdr_fmt)
                    ws.set_column(col_num, col_num, max(15, len(str(val)) + 4))
                for row_num in range(len(df)):
                    for col_num in range(len(df.columns)):
                        ws.write(row_num + 1, col_num,
                                 str(df.iloc[row_num, col_num]), cell_fmt)

            write_sheet(missing_in_target, "Missing_in_Target", red_fmt)
            write_sheet(missing_in_source, "Missing_in_Source", orange_fmt)
            write_sheet(comparison_df,     "Matched_Records",   green_fmt)

            # Summary sheet
            ws_sum = workbook.add_worksheet("Summary")
            ws_sum.set_column(0, 0, 38)
            ws_sum.set_column(1, 1, 18)
            title_fmt = workbook.add_format({"bold": True, "font_size": 14,
                                              "font_color": "#1a237e"})
            label_fmt = workbook.add_format({"bold": True, "border": 1,
                                              "bg_color": "#e8eaf6"})
            val_fmt   = workbook.add_format({"border": 1, "align": "center"})

            ws_sum.write(0, 0, "SGF Audit Reconciliation Report", title_fmt)
            ws_sum.write(1, 0, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            rows = [
                ("Total Source Records",       len(working_df)),
                ("Total Target Records",       len(df2)),
                ("Matched Records",            matched_count),
                ("Missing in Target",          len(missing_in_target)),
                ("Missing in Source",          len(missing_in_source)),
                ("Match Rate (%)",
                 f"{matched_count / max(len(working_df), 1) * 100:.1f}%"),
            ]
            for i, (label, val) in enumerate(rows, start=3):
                ws_sum.write(i, 0, label, label_fmt)
                ws_sum.write(i, 1, val,   val_fmt)

        file_name = f"SGF_Audit_Report_{timestamp}.xlsx"
        st.download_button(
            label="📥 Audit Report ကို Excel ဖြင့် ဒေါင်းလုဒ်လုပ်မည်",
            data=output.getvalue(),
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary",
        )
        st.caption(f"🗂️ File name: {file_name}")

else:
    st.info("📌 Target File ကိုတင်ပေးပါ (Step 2 ဆက်လုပ်ရန်)")
