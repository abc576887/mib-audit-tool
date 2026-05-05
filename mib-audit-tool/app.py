import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Audit Workflow Tool", layout="wide")

# --- UI Styling ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pyidaungsu&display=swap');
    body, div, span, h1, h2, h3, p { font-family: 'Pyidaungsu', sans-serif !important; }
    .step-box { border: 1px solid #ddd; padding: 20px; border-radius: 10px; background-color: #fcfcfc; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Professional Audit Workflow System")

# --- Step 1: Create Working Paper ---
st.markdown('<div class="step-box">', unsafe_allow_html=True)
st.header("Step 1: Create Audit Working Paper")
st.info("ပထမဦးစွာ Source File ကိုတင်၍ လိုအပ်သော Data ပြင်ဆင်မှုများ ပြုလုပ်ပါ။")

file_1 = st.file_uploader("Upload Source File (ဥပမာ - Production/Internal Log)", type=['xlsx', 'xls', 'xlsb'])

working_df = None
if file_1:
    # Sheet ရွေးခိုင်းမယ်
    xl1 = pd.ExcelFile(file_1)
    sheet_1 = st.selectbox("အသုံးပြုမည့် Sheet ကိုရွေးပါ (Source)", xl1.sheet_names)
    df1_raw = pd.read_excel(file_1, sheet_name=sheet_1)
    
    st.write("### Preview Raw Data", df1_raw.head(3))
    
    # Simple Cleaning/Transformation Logic
    # ဥပမာ - Column တွေ ရွေးထုတ်တာ၊ စုစုပေါင်းတွက်တာတွေ လုပ်လို့ရတယ်
    selected_cols = st.multiselect("Working Paper တွင် ပါဝင်မည့် Column များ ရွေးပါ", df1_raw.columns.tolist(), default=df1_raw.columns.tolist())
    
    if selected_cols:
        working_df = df1_raw[selected_cols].copy()
        st.success("Working Paper ပြင်ဆင်ပြီးပါပြီ။")
        st.dataframe(working_df.head(5))
st.markdown('</div>', unsafe_allow_html=True)

# --- Step 2: Reconciliation with Target File ---
st.markdown('<div class="step-box">', unsafe_allow_html=True)
st.header("Step 2: Reconciliation (တိုက်စစ်ခြင်း)")

if working_df is not None:
    file_2 = st.file_uploader("Upload Target File to Compare (ဥပမာ - Principal/Bank Report)", type=['xlsx', 'xls', 'xlsb'])
    
    if file_2:
        xl2 = pd.ExcelFile(file_2)
        sheet_2 = st.selectbox("အသုံးပြုမည့် Sheet ကိုရွေးပါ (Target)", xl2.sheet_names)
        df2 = pd.read_excel(file_2, sheet_name=sheet_2)
        
        st.divider()
        
        # Unique Key ရွေးခြင်း
        col_left, col_right = st.columns(2)
        with col_left:
            key_src = st.selectbox("Working Paper ရှိ Key Column (ID)", working_df.columns)
        with col_right:
            key_tgt = st.selectbox("Target File ရှိ Key Column (ID)", df2.columns)
            
        if st.button("စတင်တိုက်စစ်မည်"):
            # 1. Missing Analysis
            missing_in_target = working_df[~working_df[key_src].astype(str).isin(df2[key_tgt].astype(str))]
            missing_in_source = df2[~df2[key_tgt].astype(str).isin(working_df[key_src].astype(str))]
            
            # 2. Value Comparison
            # Key Column နာမည်ချင်းတူအောင် ညှိပြီး Merge လုပ်မယ်
            temp_target = df2.rename(columns={key_tgt: key_src})
            merged = pd.merge(working_df, temp_target, on=key_src, how='inner', suffixes=('_src', '_tgt'))
            
            # ဥပမာ - Amount ကွဲလွဲချက်ကို စစ်ကြည့်မယ် (Column နာမည်တူရှိရင်)
            st.subheader("Analysis Results")
            t1, t2, t3 = st.tabs(["Target တွင် မပါသောစာရင်း", "Source တွင် မပါသောစာရင်း", "စာရင်းတိုက်ဆိုင်မှု"])
            
            with t1:
                st.write(f"Missing in Target: {len(missing_in_target)}")
                st.dataframe(missing_in_target)
            with t2:
                st.write(f"Missing in Source: {len(missing_in_source)}")
                st.dataframe(missing_in_source)
            with t3:
                st.write("ဖိုင်နှစ်ခုလုံးတွင် ပါဝင်သော Data များကို နှိုင်းယှဉ်ကြည့်ခြင်း")
                st.dataframe(merged)

            # Download Report
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                missing_in_target.to_excel(writer, sheet_name='Missing_in_Target', index=False)
                missing_in_source.to_excel(writer, sheet_name='Missing_in_Source', index=False)
                merged.to_excel(writer, sheet_name='Common_Data_Comparison', index=False)
            
            st.download_button("📥 Download Final Audit Report", output.getvalue(), "audit_final_report.xlsx")

else:
    st.warning("အဆင့် (၁) ကို အရင်လုပ်ဆောင်ပါ။")
st.markdown('</div>', unsafe_allow_html=True)
