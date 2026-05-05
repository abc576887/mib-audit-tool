import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Audit Working Paper & Reconciler", layout="wide")

st.title("📑 Audit Working Paper & Binding Tool")

# --- Step 1: Upload & Data Prep ---
st.header("Step 1: Data Preparation (Working Paper ဆွဲရန်)")
uploaded_file = st.file_uploader("Working လုပ်မည့် Excel ဖိုင်ကို အရင်တင်ပါ", type=['xlsx', 'csv'], key="working")

if uploaded_file:
    # ဖိုင်ဖတ်ခြင်း
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('xlsx') else pd.read_csv(uploaded_file)
    
    st.subheader("🛠️ Working Section")
    st.write("ဖိုင်ထဲက လိုအပ်တဲ့ Column တွေကိုပဲ ရွေးထုတ်ပြီး Working ဆွဲပါ")
    
    # Column ရွေးချယ်ခြင်း (VLOOKUP မလုပ်ခင် Data ပြင်တာ)
    selected_cols = st.multiselect("အသုံးပြုမည့် Column များကို ရွေးပါ", df.columns.tolist(), default=df.columns.tolist())
    working_df = df[selected_cols].copy()
    
    # Data Cleaning (Trim spaces)
    if st.checkbox("Data များရှိ Space (နေရာလွတ်) များကို အလိုအလျောက် ဖြတ်ထုတ်မည်"):
        working_df = working_df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        st.info("Spaces cleaned!")

    st.dataframe(working_df.head(10))

    # --- Step 2: Binding & Audit ---
    st.markdown("---")
    st.header("Step 2: Final Binding & Reconciliation")
    ref_file = st.file_uploader("တိုက်စစ်မည့် Reference ဖိုင် (e.g. Bank/Vendor Statement)", type=['xlsx', 'csv'], key="ref")

    if ref_file:
        df_ref = pd.read_excel(ref_file) if ref_file.name.endswith('xlsx') else pd.read_csv(ref_file)
        
        c1, c2 = st.columns(2)
        with c1:
            key_main = st.selectbox("Working File မှ ချိတ်မည့် Key (ID)", working_df.columns)
            amt_main = st.selectbox("Working File မှ Amount Column", working_df.columns)
        with c2:
            key_ref = st.selectbox("Ref File မှ ချိတ်မည့် Key (ID)", df_ref.columns)
            amt_ref = st.selectbox("Ref File မှ Amount Column", df_ref.columns)

        if st.button("Bind and Run Audit"):
            # Binding Logic (Inner/Outer Join)
            # Working DF နဲ့ Ref DF ကို ပေါင်းခြင်း
            final_bind = pd.merge(working_df, df_ref, left_on=key_main, right_on=key_ref, how='outer', indicator=True)
            
            # Variance တွက်ခြင်း
            final_bind['Variance'] = final_bind[amt_main].fillna(0) - final_bind[amt_ref].fillna(0)

            # Results Display
            tab1, tab2, tab3 = st.tabs(["✅ Matched Records", "⚠️ Exceptions (ကွဲလွဲချက်)", "📑 Final Working Paper"])

            with tab1:
                matched = final_bind[final_bind['_merge'] == 'both']
                st.write(f"ကိုက်ညီမှုရှိသော စာရင်းပေါင်း: {len(matched)}")
                st.dataframe(matched)

            with tab2:
                st.subheader("Exception Report")
                # နှစ်ဖက်လုံးမှာ ပါသော်လည်း ပမာဏ မတူတာတွေကို အရင်ပြမယ်
                mismatch_amt = final_bind[(final_bind['_merge'] == 'both') & (final_bind['Variance'] != 0)]
                # တစ်ဖက်တည်းမှာပဲ ပါတာတွေကို ပြမယ်
                missing_records = final_bind[final_bind['_merge'] != 'both']

                st.error("ပမာဏ ကွဲလွဲနေမှုများ")
                st.dataframe(mismatch_amt)
                
                st.warning("ဖိုင်တစ်ခုတည်းတွင်သာ ပါဝင်သော စာရင်းများ")
                st.dataframe(missing_records)

            with tab3:
                st.subheader("Download Final Binded Sheet")
                # Excel အဖြစ် သိမ်းရန်
                towrite = io.BytesIO()
                final_bind.to_excel(towrite, index=False, engine='openpyxl')
                st.download_button(
                    label="Final Audit Working Paper (Excel) ကို ဒေါင်းလုဒ်လုပ်ရန်",
                    data=towrite.getvalue(),
                    file_name="Final_Audit_Working_Paper.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

else:
    st.info("Audit စတင်ရန် ပထမဦးစွာ Working ဆွဲမည့် ဖိုင်ကို Upload တင်ပေးပါ။")
