import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Multi-Sheet Audit Tool", layout="wide")

st.title("📑 Multi-Sheet Working Paper & Binding Tool")
st.info("Excel တစ်ဖိုင်တည်းမှာ Sheet အများကြီးပါရင်လည်း အဆင်ပြေအောင် ပြုလုပ်ပေးထားပါတယ်။")

# --- STEP 1: LOAD MAIN FILE & CHOOSE SHEET ---
st.header("Step 1: Main Data Preparation")
main_file = st.file_uploader("Main Excel ဖိုင်ကို တင်ပါ (Multiple Sheets support)", type=['xlsx'], key="main")

if main_file:
    # Excel ဖိုင်ထဲက Sheet နာမည်အားလုံးကို ဖတ်ခြင်း
    xl_main = pd.ExcelFile(main_file)
    sheet_names = xl_main.sheet_names
    
    selected_sheet = st.selectbox("Working ဆွဲမည့် Sheet ကို ရွေးပါ", sheet_names)
    
    # ရွေးချယ်လိုက်သော Sheet ကို Dataframe အဖြစ်ပြောင်းခြင်း
    df_main = pd.read_excel(main_file, sheet_name=selected_sheet)
    
    st.subheader(f"🛠️ Working on Sheet: [{selected_sheet}]")
    
    # Column Mapping for Working
    selected_cols = st.multiselect("အသုံးပြုမည့် Column များကို ရွေးပါ", df_main.columns.tolist(), default=df_main.columns.tolist())
    working_df = df_main[selected_cols].copy()
    
    # Cleaning Option
    if st.checkbox("Data များကို Clean လုပ်မည် (Trim Spaces)"):
        working_df = working_df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        st.success("Data cleaned!")

    st.dataframe(working_df.head(5))

    # --- STEP 2: LOAD REFERENCE FILE ---
    st.markdown("---")
    st.header("Step 2: Reference Data & Binding")
    ref_file = st.file_uploader("တိုက်စစ်မည့် Reference ဖိုင်ကို တင်ပါ", type=['xlsx', 'csv'], key="ref")

    if ref_file:
        # Ref file ကလည်း Excel ဖြစ်ခဲ့ရင် Sheet ရွေးခိုင်းမယ်
        if ref_file.name.endswith('xlsx'):
            xl_ref = pd.ExcelFile(ref_file)
            ref_sheet = st.selectbox("Reference Sheet ကို ရွေးပါ", xl_ref.sheet_names)
            df_ref = pd.read_excel(ref_file, sheet_name=ref_sheet)
        else:
            df_ref = pd.read_csv(ref_file)

        # Mapping for Binding
        col_a, col_b = st.columns(2)
        with col_a:
            st.write("**Main Working Data Settings**")
            key_main = st.selectbox("Key Column (ID/Invoice)", working_df.columns, key="km")
            amt_main = st.selectbox("Amount Column", working_df.columns, key="am")
        with col_b:
            st.write("**Reference Data Settings**")
            key_ref = st.selectbox("Key Column (ID/Invoice)", df_ref.columns, key="kr")
            amt_ref = st.selectbox("Amount Column", df_ref.columns, key="ar")

        # --- STEP 3: RUN AUDIT & BIND ---
        if st.button("🚀 Bind Sheets & Run Audit"):
            # Outer Join ဖြင့် Bind လုပ်ခြင်း
            final_bind = pd.merge(working_df, df_ref, left_on=key_main, right_on=key_ref, how='outer', indicator=True)
            
            # Variance တွက်ချက်ခြင်း
            final_bind['Variance'] = final_bind[amt_main].fillna(0) - final_bind[amt_ref].fillna(0)

            # ပြသခြင်း
            t1, t2, t3 = st.tabs(["📊 Audit Summary", "🔍 Discrepancies (မကိုက်ညီမှုများ)", "📥 Download Report"])

            with t1:
                st.subheader("Process Overview")
                c1, c2, c3 = st.columns(3)
                c1.metric("Main Records", len(working_df))
                c2.metric("Ref Records", len(df_ref))
                matches = len(final_bind[final_bind['_merge'] == 'both'])
                c3.metric("Matched", matches)
                st.dataframe(final_bind)

            with t2:
                st.subheader("Exceptions Found")
                # Amount မတူတာရှာခြင်း
                amt_diff = final_bind[(final_bind['_merge'] == 'both') & (final_bind['Variance'] != 0)]
                if not amt_diff.empty:
                    st.error(f"Amount မကိုက်ညီသော စာရင်း {len(amt_diff)} ခု တွေ့ရှိသည်။")
                    st.dataframe(amt_diff)
                
                # တစ်ဖက်တည်းမှာပဲ ရှိတာရှαခြင်း
                not_in_ref = final_bind[final_bind['_merge'] == 'left_only']
                if not_in_ref.empty:
                    st.success("Ref ဖိုင်ထဲမှာ အကုန်ပါဝင်ပါတယ်။")
                else:
                    st.warning(f"Ref ဖိုင်ထဲမှာ မပါဝင်သော စာရင်း {len(not_in_ref)} ခုရှိသည်။")
                    st.dataframe(not_in_ref)

            with t3:
                # Excel အဖြစ် သိမ်းဆည်းရန် Output ထုတ်ခြင်း
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    final_bind.to_excel(writer, sheet_name='Audit_Summary', index=False)
                    amt_diff.to_excel(writer, sheet_name='Price_Differences', index=False)
                
                st.download_button(
                    label="Final Audit Working Paper ကို ဒေါင်းလုဒ်လုပ်ရန်",
                    data=output.getvalue(),
                    file_name=f"Audit_Report_{selected_sheet}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

else:
    st.warning("⚠️ စတင်ရန်အတွက် Sheets များစွာပါဝင်သော Excel ဖိုင်ကို အပေါ်တွင် အရင် တင်ပေးပါ။")
