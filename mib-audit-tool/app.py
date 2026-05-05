import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="MIB Audit Tool", layout="wide")
st.title("🛡️ Professional Audit Tool (Enhanced Table Support)")

# --- STEP 1: LOAD MAIN FILE ---
st.header("Step 1: Main Data Preparation")
main_file = st.file_uploader("Main Excel File တင်ပါ", type=['xlsx'], key="main")

if main_file:
    xl_main = pd.ExcelFile(main_file)
    selected_sheet = st.selectbox("Working Sheet ရွေးပါ", xl_main.sheet_names)
    
    # Table Column တွေက Row အောက်မှာ ရှိနေရင် ကျော်ဖတ်ရန် (Skip Rows/Header Row)
    header_row = st.number_input("Header စတင်သည့် Row နံပါတ် (Excel Row - 1)", min_value=0, value=0, help="Excel ရဲ့ Row 1 မှာ Header မရှိရင် ဒီမှာ ပြင်ပေးပါ။")
    
    # Load Data with specific header
    df_main = pd.read_excel(main_file, sheet_name=selected_sheet, header=header_row)
    
    st.subheader(f"🛠️ Working on: {selected_sheet}")
    selected_cols = st.multiselect("အသုံးပြုမည့် Column များကို ရွေးပါ", df_main.columns.tolist(), default=df_main.columns.tolist())
    working_df = df_main[selected_cols].copy()
    st.dataframe(working_df.head(5))

    # --- STEP 2: LOAD REFERENCE FILE ---
    st.markdown("---")
    st.header("Step 2: Reference Data & Binding")
    ref_file = st.file_uploader("Reference File တင်ပါ", type=['xlsx', 'csv'], key="ref")

    if ref_file:
        if ref_file.name.endswith('xlsx'):
            xl_ref = pd.ExcelFile(ref_file)
            ref_sheet = st.selectbox("Reference Sheet ရွေးပါ", xl_ref.sheet_names)
            ref_header = st.number_input("Ref Header Row နံပါတ်", min_value=0, value=0, key="ref_h")
            df_ref = pd.read_excel(ref_file, sheet_name=ref_sheet, header=ref_header)
        else:
            df_ref = pd.read_csv(ref_file)

        # Mapping
        c1, c2 = st.columns(2)
        with c1:
            key_main = st.selectbox("Key Column (ID)", working_df.columns, key="km")
            amt_main = st.selectbox("Amount Column", working_df.columns, key="am")
        with c2:
            key_ref = st.selectbox("Key Column (ID)", df_ref.columns, key="kr")
            amt_ref = st.selectbox("Amount Column", df_ref.columns, key="ar")

        # --- STEP 3: RUN AUDIT ---
        if st.button("🚀 Bind & Run Audit"):
            try:
                # Type Fix: ID များကို စာသားပြောင်းပြီး Trim လုပ်ခြင်း
                working_df[key_main] = working_df[key_main].astype(str).str.strip().replace('nan', '')
                df_ref[key_ref] = df_ref[key_ref].astype(str).str.strip().replace('nan', '')
                
                # Merge
                final_bind = pd.merge(working_df, df_ref, left_on=key_main, right_on=key_ref, how='outer', indicator=True)
                
                # Numeric Fix: Amount များကို နံပါတ်ပြောင်းခြင်း
                final_bind['Variance'] = pd.to_numeric(final_bind[amt_main], errors='coerce').fillna(0) - \
                                         pd.to_numeric(final_bind[amt_ref], errors='coerce').fillna(0)

                # Tabs
                t1, t2, t3 = st.tabs(["📊 Summary", "🔍 Discrepancies", "📥 Export"])

                with t1:
                    st.metric("Matches", len(final_bind[final_bind['_merge'] == 'both']))
                    st.dataframe(final_bind)

                with t2:
                    # Difference filters
                    diff_amt = final_bind[(final_bind['_merge'] == 'both') & (final_bind['Variance'] != 0)]
                    if not diff_amt.empty:
                        st.error(f"Amount Difference: {len(diff_amt)}")
                        st.dataframe(diff_amt)
                    
                    missing = final_bind[final_bind['_merge'] != 'both']
                    st.warning(f"Unmatched Records: {len(missing)}")
                    st.dataframe(missing)

                with t3:
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        final_bind.to_excel(writer, sheet_name='Full_Report', index=False)
                    
                    st.download_button("Download Report", output.getvalue(), "Audit_Report.xlsx")

            except Exception as e:
                st.error(f"Error: {e}")
