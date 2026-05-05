import streamlit as st
import pandas as pd
import io

# Page Config
st.set_page_config(page_title="MIB Audit & Reconciliation Tool", layout="wide")

st.title("🛡️ Professional Audit Working Paper & Binding Tool")
st.markdown("---")

# --- STEP 1: LOAD MAIN FILE ---
st.header("Step 1: Main Data Preparation (Working Sheet)")
main_file = st.file_uploader("Main Excel File တင်ပါ", type=['xlsx'], key="main")

if main_file:
    xl_main = pd.ExcelFile(main_file)
    selected_sheet = st.selectbox("Working ဆွဲမည့် Sheet ကို ရွေးပါ", xl_main.sheet_names)
    
    # Load Sheet
    df_main = pd.read_excel(main_file, sheet_name=selected_sheet)
    
    st.subheader(f"🛠️ Working on: {selected_sheet}")
    
    # Select Columns to keep
    selected_cols = st.multiselect("အသုံးပြုမည့် Column များကို ရွေးပါ", df_main.columns.tolist(), default=df_main.columns.tolist())
    working_df = df_main[selected_cols].copy()
    
    st.dataframe(working_df.head(5))

    # --- STEP 2: LOAD REFERENCE FILE ---
    st.markdown("---")
    st.header("Step 2: Reference Data & Binding")
    ref_file = st.file_uploader("တိုက်စစ်မည့် Reference File (e.g. Bank Statement) တင်ပါ", type=['xlsx', 'csv'], key="ref")

    if ref_file:
        if ref_file.name.endswith('xlsx'):
            xl_ref = pd.ExcelFile(ref_file)
            ref_sheet = st.selectbox("Reference Sheet ကို ရွေးပါ", xl_ref.sheet_names)
            df_ref = pd.read_excel(ref_file, sheet_name=ref_sheet)
        else:
            df_ref = pd.read_csv(ref_file)

        # Mapping Columns
        c1, c2 = st.columns(2)
        with c1:
            st.info("Main Sheet Settings")
            key_main = st.selectbox("Key Column (ID/Invoice)", working_df.columns, key="km")
            amt_main = st.selectbox("Amount Column", working_df.columns, key="am")
        with c2:
            st.info("Reference Sheet Settings")
            key_ref = st.selectbox("Key Column (ID/Invoice)", df_ref.columns, key="kr")
            amt_ref = st.selectbox("Amount Column", df_ref.columns, key="ar")

        # --- STEP 3: RUN AUDIT ---
        if st.button("🚀 Bind Sheets & Run Audit"):
            try:
                # CRITICAL FIX: Convert keys to string and strip spaces to avoid ValueError
                working_df[key_main] = working_df[key_main].astype(str).str.strip()
                df_ref[key_ref] = df_ref[key_ref].astype(str).str.strip()
                
                # Merge (VLOOKUP Logic)
                final_bind = pd.merge(working_df, df_ref, left_on=key_main, right_on=key_ref, how='outer', indicator=True)
                
                # Calculate Variance
                final_bind['Variance'] = pd.to_numeric(final_bind[amt_main], errors='coerce').fillna(0) - \
                                         pd.to_numeric(final_bind[amt_ref], errors='coerce').fillna(0)

                # Results Display
                t1, t2, t3 = st.tabs(["📊 Summary", "🔍 Discrepancies", "📥 Download Report"])

                with t1:
                    st.subheader("Audit Overview")
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Main Records", len(working_df))
                    m2.metric("Ref Records", len(df_ref))
                    matches = len(final_bind[final_bind['_merge'] == 'both'])
                    m3.metric("Fully Reconciled", matches)
                    st.dataframe(final_bind)

                with t2:
                    st.subheader("Exceptions Found")
                    # 1. Amount Mismatch
                    amt_diff = final_bind[(final_bind['_merge'] == 'both') & (final_bind['Variance'] != 0)]
                    if not amt_diff.empty:
                        st.error(f"Amount မကိုက်ညီသော စာရင်း: {len(amt_diff)} ခု")
                        st.dataframe(amt_diff)
                    
                    # 2. Missing in Ref
                    missing_ref = final_bind[final_bind['_merge'] == 'left_only']
                    if not missing_ref.empty:
                        st.warning(f"Reference ဖိုင်ထဲတွင် မပါသော စာရင်း: {len(missing_ref)} ခု")
                        st.dataframe(missing_ref)

                with t3:
                    # Export to Excel
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        final_bind.to_excel(writer, sheet_name='Full_Audit_Trail', index=False)
                        if not amt_diff.empty:
                            amt_diff.to_excel(writer, sheet_name='Price_Mismatch', index=False)
                        if not missing_ref.empty:
                            missing_ref.to_excel(writer, sheet_name='Missing_in_Ref', index=False)
                    
                    st.download_button(
                        label="Final Audit Working Paper ကို Download လုပ်ရန်",
                        data=output.getvalue(),
                        file_name=f"Audit_Result_{selected_sheet}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            except Exception as e:
                st.error(f"Error Occurred: {str(e)}")
                st.info("အကြံပြုချက်: Column နာမည်များ မှန်ကန်စွာ ရွေးချယ်ထားကြောင်း ပြန်စစ်ပေးပါ။")

else:
    st.info("စတင်ရန် Excel ဖိုင်ကို အပေါ်တွင် တင်ပေးပါ။")
