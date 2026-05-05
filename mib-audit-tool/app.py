import streamlit as st
import pandas as pd
import io
import plotly.express as px

# Professional Theme Configuration
st.set_page_config(
    page_title="AuditLink Pro | Internal Audit Suite",
    page_icon="🛡️",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { border: 1px solid #dee2e6; padding: 15px; border-radius: 10px; background: white; }
    .audit-header { color: #1e3a8a; font-weight: bold; border-bottom: 2px solid #1e3a8a; padding-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: စစ်ဆေးမှု ထိန်းချုပ်ခန်း ---
with st.sidebar:
    st.title("🛡️ Audit Controls")
    st.markdown("### ⚙️ ကန့်သတ်ချက်များ သတ်မှတ်ရန်")
    
    # Materiality Threshold သတ်မှတ်ခြင်း
    threshold = st.number_input("လက်ခံနိုင်သော ကွဲလွဲမှု ပမာဏ (Materiality)", value=0.0, step=0.01)
    
    st.markdown("---")
    st.info("""
    💡 **Auditor Tip:** 
    စာရင်းမတိုက်စစ်မီ ပင်မ Ledger ထဲတွင် Duplicate (စာရင်းထပ်နေခြင်း) ရှိမရှိကို အရင်စစ်ဆေးပါ။
    """)

# --- MAIN INTERFACE ---
st.markdown("<h1 class='audit-header'>🛡️ Professional Internal Audit System</h1>", unsafe_allow_html=True)

# ၁။ Data တင်သွင်းခြင်း (Ingestion)
col1, col2 = st.columns(2)
with col1:
    st.markdown("#### 📁 အဆင့် (၁): ပင်မစာရင်းဖိုင် (Main Ledger)")
    main_file = st.file_uploader("Ledger တင်ရန် (XLSX, XLS, CSV)", type=['xlsx', 'xls', 'csv'], key="main")
with col2:
    st.markdown("#### 📁 အဆင့် (၂): တိုက်စစ်မည့်ဖိုင် (Statement/Reference)")
    ref_file = st.file_uploader("Reference တင်ရန် (XLSX, XLS, CSV)", type=['xlsx', 'xls', 'csv'], key="ref")

@st.cache_data
def load_data(file):
    if file is None: return None
    try:
        if file.name.endswith('.csv'):
            return pd.read_csv(file, encoding='utf-8-sig')
        return pd.read_excel(file)
    except Exception as e:
        st.error(f"ဖိုင်ဖတ်ရာတွင် အမှားရှိနေပါသည်: {e}")
        return None

df_main = load_data(main_file)
df_ref = load_data(ref_file)

if df_main is not None and df_ref is not None:
    # ၂။ Column Mapping UI
    with st.expander("🔗 Field Mapping - ကော်လံများ ချိတ်ဆက်ခြင်း", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        with c1: key_main = st.selectbox("ID/Voucher Column (Source)", df_main.columns)
        with c2: key_ref = st.selectbox("ID/Voucher Column (Target)", df_ref.columns)
        with c3: amt_main = st.selectbox("Amount Column (Source)", df_main.columns)
        with c4: amt_ref = st.selectbox("Amount Column (Target)", df_ref.columns)

    if st.button("🚀 စစ်ဆေးမှု စတင်မည်", use_container_width=True):
        # Data Cleaning
        df_main[key_main] = df_main[key_main].astype(str).str.strip()
        df_ref[key_ref] = df_ref[key_ref].astype(str).str.strip()

        # အဆင့်မြင့် Reconciliation Logic
        recon = pd.merge(df_main, df_ref, left_on=key_main, right_on=key_ref, how='outer', indicator=True)
        recon['Difference'] = recon[amt_main].fillna(0) - recon[amt_ref].fillna(0)
        
        # Exceptions ခွဲထုတ်ခြင်း
        matched = recon[recon['_merge'] == 'both']
        missing_in_ref = recon[recon['_merge'] == 'left_only']
        missing_in_main = recon[recon['_merge'] == 'right_only']
        material_variances = matched[matched['Difference'].abs() > threshold]

        # ၃။ Dashboard ပြသခြင်း
        st.markdown("### 📊 စစ်ဆေးမှု ရလဒ် ခြုံငုံသုံးသပ်ချက်")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("ကိုက်ညီသော စာရင်း", len(matched))
        m2.metric("ကျန်ခဲ့သော စာရင်း (Missing)", len(missing_in_ref))
        m3.metric("ပမာဏ ကွဲလွဲမှု (Variance)", len(material_variances))
        m4.metric("အန္တရာယ်ရှိနိုင်သော စာရင်း (Risk)", len(missing_in_ref) + len(material_variances))

        # Chart ပြသခြင်း
        fig = px.pie(values=[len(matched), len(missing_in_ref), len(material_variances)], 
                     names=['Full Match', 'Missing Records', 'Amount Variance'],
                     color_discrete_sequence=['#10b981', '#ef4444', '#f59e0b'],
                     hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

        # ၄။ အသေးစိတ် Exception Tabs
        tab1, tab2, tab3, tab4 = st.tabs(["💰 ပမာဏ ကွဲလွဲချက်များ", "🚩 ကျန်ခဲ့သော စာရင်းများ", "👯 Double Entry စစ်ဆေးချက်", "📜 မှတ်တမ်းအပြည့်အစုံ"])
        
        with tab1:
            st.warning("သတ်မှတ်ထားသော Materiality ထက် ပိုနေသော ကွဲလွဲချက်များ")
            st.dataframe(material_variances[[key_main, amt_main, amt_ref, 'Difference']])

        with tab2:
            st.error("တစ်ဖက်ဖက်တွင် ကျန်ခဲ့သော စာရင်းများ")
            ca, cb = st.columns(2)
            ca.write("**Main Ledger တွင်သာ ရှိသောစာရင်း**")
            ca.dataframe(missing_in_ref)
            cb.write("**Reference တွင်သာ ရှိသောစာရင်း**")
            cb.dataframe(missing_in_main)

        with tab3:
            st.info("ပင်မစာရင်းတွင် ID တူပြီး ထပ်နေသော စာရင်းများ")
            dupes = df_main[df_main.duplicated(subset=[key_main], keep=False)]
            st.dataframe(dupes)

        with tab4:
            st.write("တိုက်စစ်ထားသော စာရင်းမှတ်တမ်း အပြည့်အစုံ")
            st.dataframe(recon)

        # ၅။ Report ထုတ်ယူခြင်း
        st.markdown("---")
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            recon.to_excel(writer, sheet_name='Audit_Trail', index=False)
            material_variances.to_excel(writer, sheet_name='Exceptions', index=False)
            dupes.to_excel(writer, sheet_name='Duplicates', index=False)
        
        st.download_button(
            label="📥 Audit Report (Excel) ထုတ်ယူရန်",
            data=output.getvalue(),
            file_name="Audit_Report_Myanmar.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
else:
    st.markdown("""
    ### 🔰 အသုံးပြုနည်း လမ်းညွှန်
    1. **ပင်မစာရင်း** နှင့် **တိုက်စစ်မည့်ဖိုင်** ကို အပေါ်တွင် Upload တင်ပါ။
    2. ကော်လံအမည်များကို မှန်ကန်စွာ ချိတ်ဆက်ပေးပါ။
    3. **Execute** ခလုတ်ကို နှိပ်ပြီး Dashboard တွင် ရလဒ်များ ကြည့်ရှုပါ။
    4. လိုအပ်ပါက **Excel Report** ကို ဒေါင်းလုဒ်ဆွဲ၍ စာရင်းစစ် အထောက်အထားအဖြစ် သိမ်းဆည်းပါ။
    """)
