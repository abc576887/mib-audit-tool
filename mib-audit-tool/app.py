import streamlit as st
import pandas as pd
from thefuzz import process, fuzz
import io

# Page Configuration
st.set_page_config(page_title="Professional Audit Tool", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Advanced Internal Audit Automation Tool")
st.write("Excel ဖိုင်များကို တိုက်စစ်ရန်နှင့် မှားယွင်းမှုများကို ရှာဖွေရန်အတွက် Professional Tool")

# --- SIDEBAR SETTINGS ---
st.sidebar.header("⚙️ Audit Settings")
fuzzy_score = st.sidebar.slider("Fuzzy Match Sensitivity (စာလုံးပေါင်းတူညီမှု %)", 0, 100, 80)
st.sidebar.info("Hint: 80% သည် စာလုံးပေါင်း အနည်းငယ်မှားသော်လည်း တူညီသည်ဟု ယူဆရန် အကောင်းဆုံးဖြစ်သည်။")

# --- FILE UPLOADER ---
col1, col2 = st.columns(2)
with col1:
    main_file = st.file_uploader("တင်သွင်းမည့်ဖိုင် (Main File - e.g., Ledger)", type=['xlsx', 'csv'])
with col2:
    ref_file = st.file_uploader("နှိုင်းယှဉ်မည့်ဖိုင် (Reference File - e.g., Bank Statement)", type=['xlsx', 'csv'])

if main_file and ref_file:
    # Load Data
    try:
        df_main = pd.read_excel(main_file) if main_file.name.endswith('xlsx') else pd.read_csv(main_file)
        df_ref = pd.read_excel(ref_file) if ref_file.name.endswith('xlsx') else pd.read_csv(ref_file)
    except Exception as e:
        st.error(f"Error loading files: {e}")
        st.stop()

    st.markdown("---")
    
    # --- COLUMN MAPPING ---
    st.subheader("🔗 Step 1: Column Mapping")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        main_key = st.selectbox("Main File မှ Key Column (ID/Invoice)", df_main.columns)
    with c2:
        ref_key = st.selectbox("Ref File မှ Key Column (ID/Invoice)", df_ref.columns)
    with c3:
        main_amt = st.selectbox("Main File မှ Amount Column", df_main.columns)
    with c4:
        ref_amt = st.selectbox("Ref File မှ Amount Column", df_ref.columns)

    if st.button("🚀 Start Audit Process"):
        # --- DATA CLEANING ---
        df_main[main_key] = df_main[main_key].astype(str).str.strip()
        df_ref[ref_key] = df_ref[ref_key].astype(str).str.strip()

        # --- AUDIT LOGIC ---
        
        # 1. VLOOKUP / Merge Logic
        merged = pd.merge(df_main, df_ref, left_on=main_key, right_on=ref_key, how='outer', indicator=True)

        # 2. Amount Difference Calculation
        merged['Difference'] = merged[main_amt].fillna(0) - merged[ref_amt].fillna(0)

        # 3. Duplicate Detection
        dups_main = df_main[df_main.duplicated(subset=[main_key], keep=False)]

        # --- DISPLAY RESULTS ---
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Summary", "❌ Missing Records", "💰 Variance (Amount)", "👯 Duplicates", "🔍 Fuzzy Match Help"])

        with tab1:
            st.subheader("Audit Overview")
            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("Total Ledger Items", len(df_main))
            mc2.metric("Total Ref Items", len(df_ref))
            reconciled = len(merged[merged['_merge'] == 'both'])
            mc3.metric("Match ဖြစ်သောအရေအတွက်", reconciled)

        with tab2:
            st.subheader("တွေ့ရှိချက် - ဖိုင်တစ်ခုတွင်သာ ပါဝင်သော အချက်အလက်များ")
            missing_in_ref = merged[merged['_merge'] == 'left_only']
            missing_in_main = merged[merged['_merge'] == 'right_only']
            
            st.write("**Main File တွင်ရှိပြီး Ref File တွင် မရှိသော အချက်အလက်များ:**")
            st.dataframe(missing_in_ref)
            
            st.write("**Ref File တွင်ရှိပြီး Main File တွင် မရှိသော အချက်အလက်များ:**")
            st.dataframe(missing_in_main)

        with tab3:
            st.subheader("တွေ့ရှိချက် - ပမာဏ ကွဲလွဲနေမှုများ")
            variances = merged[(merged['_merge'] == 'both') & (merged['Difference'] != 0)]
            if not variances.empty:
                st.warning(f"ပမာဏ ကွဲလွဲနေသော စာရင်း {len(variances)} ခု တွေ့ရှိပါသည်။")
                st.dataframe(variances[[main_key, main_amt, ref_amt, 'Difference']])
            else:
                st.success("ပမာဏအားလုံး ကိုက်ညီပါသည်။")

        with tab4:
            st.subheader("တွေ့ရှိချက် - Duplicate Entries (Double Entry)")
            if not dups_main.empty:
                st.error(f"Main File ထဲတွင် Duplicate ဖြစ်နေသော ID {len(dups_main)} ခု တွေ့ရှိပါသည်။")
                st.dataframe(dups_main)
            else:
                st.success("Duplicate entries မတွေ့ရှိပါ။")

        with tab5:
            st.subheader("Fuzzy Matching (အနီးစပ်ဆုံး တိုက်စစ်ခြင်း)")
            st.info("ID မတူသော်လည်း စာသား အနီးစပ်ဆုံး တူညီမှုများကို ရှာဖွေပေးသည်။ (ဥပမာ- 'Apple Inc' နှင့် 'Apple Incorporated')")
            
            # Fuzzy matching logic for unmatched records
            unmatched_main = df_main[~df_main[main_key].isin(df_ref[ref_key])][main_key].tolist()
            choices = df_ref[ref_key].tolist()
            
            fuzzy_results = []
            if unmatched_main and choices:
                for item in unmatched_main[:50]: # Performance အတွက် ၅၀ ခုပဲ အရင်ပြမယ်
                    match, score = process.extractOne(item, choices, scorer=fuzz.token_sort_ratio)
                    if score >= fuzzy_score:
                        fuzzy_results.append({"Main Key": item, "Suggested Match": match, "Confidence Score": score})
            
            if fuzzy_results:
                st.table(fuzzy_results)
            else:
                st.write("နီးစပ်သော အချက်အလက်များ မတွေ့ပါ။")

        # --- EXPORT REPORT ---
        st.markdown("---")
        st.subheader("📥 Export Audit Report")
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            merged.to_excel(writer, sheet_name='Full_Audit_Report', index=False)
            if not variances.empty: variances.to_excel(writer, sheet_name='Variances', index=False)
            if not dups_main.empty: dups_main.to_excel(writer, sheet_name='Duplicates', index=False)
            
        st.download_button(
            label="Audit Result ကို Excel ဖြင့် ဒေါင်းလုဒ်လုပ်ရန်",
            data=output.getvalue(),
            file_name="Audit_Report_Final.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.warning("စတင်ရန်အတွက် ဘယ်ဘက်နှင့် ညာဘက်တွင် Excel ဖိုင်များကို Upload တင်ပေးပါ။")
