import streamlit as st
import pandas as pd
import io
import plotly.express as px

# Professional Theme Configuration
st.set_page_config(page_title="Auditor-Pro | Precision Edition", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    .stMetric { border-left: 5px solid #1e3a8a; background: white; padding: 15px; border-radius: 10px; }
    h1 { color: #1e3a8a; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Auditor-Pro: Precision Audit & Rounding Analysis")

# --- SIDEBAR: AUDIT CONTROLS ---
with st.sidebar:
    st.header("⚙️ Precision Settings")
    # Rounding Finder အတွက် Control
    st.subheader("Rounding Analysis")
    min_rounding = st.number_input("အနည်းဆုံး ကွဲလွဲမှု (Min Difference)", value=0.01, format="%.2f")
    max_rounding = st.number_input("အများဆုံး ကွဲလွဲမှု (Max Difference)", value=1000.0, format="%.2f")
    
    st.divider()
    st.info("💡 **Auditor Tip:** Rounding အသေးလေးတွေဟာ Exchange Rate ကြောင့် ဖြစ်နိုင်သလို၊ Rounding အကြီးကြီးတွေဟာ စာရင်းမှားယွင်းမှု (သို့မဟုတ်) လိမ်လည်မှု ဖြစ်နိုင်ပါတယ်။")

# --- DATA LOADING ---
def load_data(file):
    if file is None: return None
    ext = file.name.split('.')[-1].lower()
    try:
        if ext == 'csv': return pd.read_csv(file, encoding='utf-8-sig')
        elif ext == 'xls': return pd.read_excel(file, engine='xlrd')
        else: return pd.read_excel(file, engine='openpyxl')
    except Exception as e:
        st.error(f"Error: {e}")
        return None

col1, col2 = st.columns(2)
with col1:
    main_file = st.file_uploader("📁 ပင်မစာရင်း (Main Ledger)", type=['xlsx', 'xls', 'csv'])
with col2:
    ref_file = st.file_uploader("📁 တိုက်စစ်မည့်စာရင်း (Reference)", type=['xlsx', 'xls', 'csv'])

if main_file and ref_file:
    df_main = load_data(main_file)
    df_ref = load_data(ref_file)

    with st.expander("🔗 Column Mapping", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        key_main = c1.selectbox("ID/Voucher (Source)", df_main.columns)
        key_ref = c2.selectbox("ID/Voucher (Target)", df_ref.columns)
        amt_main = c3.selectbox("Amount (Source)", df_main.columns)
        amt_ref = c4.selectbox("Amount (Target)", df_ref.columns)

    if st.button("🚀 Run Precision Audit Analysis", use_container_width=True):
        # Data Pre-processing
        df_main[key_main] = df_main[key_main].astype(str).str.strip()
        df_ref[key_ref] = df_ref[key_ref].astype(str).str.strip()

        # Reconciliation Logic
        recon = pd.merge(df_main, df_ref, left_on=key_main, right_on=key_ref, how='outer', indicator=True)
        recon['Variance'] = (recon[amt_main].fillna(0) - recon[amt_ref].fillna(0)).round(4)
        recon['Abs_Variance'] = recon['Variance'].abs()

        # 1. Rounding Analysis Logic
        # အသေးအမွှား rounding နှင့် အကြီးစား rounding များကို ခွဲထုတ်ခြင်း
        rounding_issues = recon[(recon['_merge'] == 'both') & 
                                (recon['Abs_Variance'] >= min_rounding) & 
                                (recon['Abs_Variance'] <= max_rounding)]
        
        big_issues = recon[(recon['_merge'] == 'both') & (recon['Abs_Variance'] > max_rounding)]

        # Dashboard
        st.divider()
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Fully Matched", len(recon[recon['Variance'] == 0]))
        m2.metric("Rounding Issues", len(rounding_issues))
        m3.metric("Big Variance (High Risk)", len(big_issues))
        m4.metric("Missing Entries", len(recon[recon['_merge'] != 'both']))

        # Tabs for Findings
        tab1, tab2, tab3 = st.tabs(["🔎 Rounding & Small Diff", "🚨 High Risk Variances", "📊 Data Distribution"])

        with tab1:
            st.write(f"### ပမာဏ {min_rounding} နှင့် {max_rounding} ကြားရှိသော ကွဲလွဲချက်များ")
            st.dataframe(rounding_issues[[key_main, amt_main, amt_ref, 'Variance']])

        with tab2:
            st.error(f"### ပမာဏ {max_rounding} ထက်ကျော်သော အကြီးစား ကွဲလွဲချက်များ")
            st.dataframe(big_issues[[key_main, amt_main, amt_ref, 'Variance']])

        with tab3:
            st.write("### Variance Distribution Chart")
            fig = px.scatter(recon[recon['_merge'] == 'both'], x=key_main, y="Variance", 
                             color="Abs_Variance", size="Abs_Variance",
                             title="Visualizing All Discrepancies (Big & Small)")
            st.plotly_chart(fig, use_container_width=True)

        # Download Report
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            recon.to_excel(writer, sheet_name='Full_Log', index=False)
            rounding_issues.to_excel(writer, sheet_name='Rounding_Issues', index=False)
            big_issues.to_excel(writer, sheet_name='Major_Exceptions', index=False)

        st.download_button("📥 Download Precision Audit Report", output.getvalue(), 
                           "Precision_Audit_Report.xlsx", use_container_width=True)

else:
    st.info("💡 စတင်ရန် ဖိုင်များကို Upload တင်ပါ။ Sidebar တွင် Rounding အကွာအဝေးကို သတ်မှတ်နိုင်ပါသည်။")
