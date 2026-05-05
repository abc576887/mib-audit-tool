import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="SGF Audit Workflow Tool", layout="wide")

# UI Style (Myanmar Unicode Support)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pyidaungsu&display=swap');
    html, body, [class*="css"] { font-family: 'Pyidaungsu', sans-serif; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #007bff; color: white; }
    .step-header { background-color: #e9ecef; padding: 10px; border-radius: 5px; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ SGF Raw Data Audit Workflow")

# Step 1: Create Working Paper
st.markdown('<div class="step-header"><h3>Step 1: Create Working Paper (Source)</h3></div>', unsafe_allow_html=True)
file_1 = st.file_uploader("SGF Raw File ကိုတင်ပါ (ဥပမာ - SGF Raw (1-2025).xlsx)", type=['xlsx', 'xls', 'xlsb'])

working_df = None

if file_1:
    xl1 = pd.ExcelFile(file_1)
    sheet_name = st.selectbox("Working ဆွဲမည့် Sheet ကိုရွေးပါ", xl1.sheet_names)
    
    # Header Row ကို User က ရွေးလို့ရအောင် လုပ်ထားပေးတယ် (SGF File မှာ Row 1 က Header ဖြစ်လေ့ရှိလို့)
    header_row = st.number_input("Header Row နံပါတ် (ပုံမှန်အားဖြင့် 1)", value=1)
    df1_raw = pd.read_excel(file_1, sheet_name=sheet_name, header=header_row)
    
    st.write("#### Data Preview")
    st.dataframe(df1_raw.head(5))
    
    # Working Paper ပြင်ဆင်ခြင်း (Column ရွေးထုတ်ခြင်း)
    selected_cols = st.multiselect("Working Paper အတွက် လိုအပ်သော Column များရွေးပါ", df1_raw.columns.tolist(), default=df1_raw.columns.tolist()[:5])
    
    if selected_cols:
        working_df = df1_raw[selected_cols].copy()
        # Clean data (NaN ဖယ်တာမျိုး လုပ်နိုင်တယ်)
        if st.checkbox("စာကြောင်းအလွတ် (Empty Rows) များဖယ်ထုတ်မည်"):
            working_df.dropna(how='all', inplace=True)
            
        st.success(f"Working Paper အဆင်သင့်ဖြစ်ပါပြီ။ စုစုပေါင်းစာရင်း: {len(working_df)} ခု")

st.markdown("---")

# Step 2: Reconciliation
st.markdown('<div class="step-header"><h3>Step 2: Reconciliation (တိုက်စစ်ခြင်း)</h3></div>', unsafe_allow_html=True)

if working_df is not None:
    file_2 = st.file_uploader("နှိုင်းယှဉ်မည့် Target File ကိုတင်ပါ", type=['xlsx', 'xls', 'xlsb'])
    
    if file_2:
        xl2 = pd.ExcelFile(file_2)
        sheet_name_2 = st.selectbox("Target Sheet ကိုရွေးပါ", xl2.sheet_names)
        df2 = pd.read_excel(file_2, sheet_name=sheet_name_2, header=header_row)
        
        col1, col2 = st.columns(2)
        with col1:
            key_src = st.selectbox("Working Paper ရှိ Key (ID/Code)", working_df.columns)
        with col2:
            key_tgt = st.selectbox("Target File ရှိ Key (ID/Code)", df2.columns)
            
        if st.button("🚀 တိုက်စစ်မည်"):
            # 1. Missing Data ရှာဖွေခြင်း
            missing_in_target = working_df[~working_df[key_src].astype(str).isin(df2[key_tgt].astype(str))]
            missing_in_source = df2[~df2[key_tgt].astype(str).isin(working_df[key_src].astype(str))]
            
            # 2. Comparison Table
            df2_renamed = df2.rename(columns={key_tgt: key_src})
            comparison_df = pd.merge(working_df, df2_renamed, on=key_src, how='inner', suffixes=('_Working', '_Target'))

            # Result Display
            tab1, tab2, tab3 = st.tabs(["Target မှာမပါတာ", "Working မှာမပါတာ", "Data ကိုက်ညီမှု"])
            
            with tab1:
                st.error(f"Target ဖိုင်ထဲမှာ မတွေ့ရတဲ့ စာရင်း {len(missing_in_target)} ခု")
                st.dataframe(missing_in_target)
            
            with tab2:
                st.warning(f"Working Paper မှာ မပါတဲ့ စာရင်း {len(missing_in_source)} ခု")
                st.dataframe(missing_in_source)
                
            with tab3:
                st.write("နှစ်ဖိုင်လုံးမှာပါတဲ့ Data များကို တွဲပြထားခြင်း")
                st.dataframe(comparison_df)

            # Excel Report ထုတ်ခြင်း
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                missing_in_target.to_excel(writer, sheet_name='Missing_in_Target', index=False)
                missing_in_source.to_excel(writer, sheet_name='Missing_in_Source', index=False)
                comparison_df.to_excel(writer, sheet_name='Comparison_Result', index=False)
            
            st.download_button(
                label="📥 Audit Report ကို Excel ဖြင့် ဒေါင်းလုဒ်လုပ်မည်",
                data=output.getvalue(),
                file_name="Audit_Findings.xlsx"
            )
else:
    st.info("အဆင့် (၁) တွင် Source File ကို အရင်တင်ပေးပါ။")
