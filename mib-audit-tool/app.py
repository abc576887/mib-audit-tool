import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="SGF Smart Audit", layout="wide")

st.title("🛡️ Stock Balance Audit Tool")
st.markdown("---")

# --- STEP 1: LOAD MAIN FILE ---
st.header("Step 1: Stock Balance Data Preparation")
main_file = st.file_uploader("Main Excel File (SGF Raw) ကိုတင်ပါ", type=['xlsx'], key="main")

if main_file:
    xl_main = pd.ExcelFile(main_file)
    selected_sheet = st.selectbox("Working ဆွဲမည့် Sheet ကို ရွေးပါ (e.g., Warehouse)", xl_main.sheet_names)
    
    # 💡 ပုံအရ Header က Row 4 မှာ ရှိတဲ့အတွက် header=3 လို့ သတ်မှတ်ပါတယ်
    # Excel Table Style ဖြစ်နေရင် header index က အရမ်းအရေးကြီးပါတယ်
    df_main = pd.read_excel(main_file, sheet_name=selected_sheet, header=3)
    
    # Column နာမည်တွေထဲမှာ Space ပါနေရင် ဖြတ်ပစ်မယ်
    df_main.columns = [str(c).strip() for c in df_main.columns]
    
    st.subheader(f"🛠️ Column Selection from Table")
    
    # ပုံထဲကအတိုင်း Code, Description, Unit ကို အဓိကထား ရွေးပါမယ်
    all_cols = df_main.columns.tolist()
    target_cols = [c for c in ["Code", "Description", "Unit", "Opening", "Total Received"] if c in all_cols]
    
    selected_cols = st.multiselect("Working Paper တွင် အသုံးပြုမည့် Column များ", all_cols, default=target_cols)
    
    if selected_cols:
        # Data Preparation
        working_df = df_main[selected_cols].copy()
        
        # 💡 Table အောက်ခြေက Total Row တွေ ဒါမှမဟုတ် Empty Row တွေကို ဖယ်ဖို့
        # Code (Key) မပါတဲ့ Row တွေကို ဖြုတ်ပစ်မယ်
        working_df = working_df.dropna(subset=[selected_cols[0]])
        
        st.write("Preview Working Data:")
        st.dataframe(working_df.head(10))

        # --- STEP 2: LOAD REFERENCE FILE ---
        st.markdown("---")
        st.header("Step 2: Reference & Binding (VLOOKUP Style)")
        ref_file = st.file_uploader("တိုက်စစ်မည့် Reference File (e.g., P Average) ကိုတင်ပါ", type=['xlsx'], key="ref")

        if ref_file:
            xl_ref = pd.ExcelFile(ref_file)
            ref_sheet = st.selectbox("Reference Sheet ကို ရွေးပါ", xl_ref.sheet_names)
            
            # Ref ဖိုင်က Header Row ကို ရွေးခိုင်းမယ် (ပုံမှန်အားဖြင့် Row 1 ဖြစ်တတ်ပါတယ်)
            ref_header = st.number_input("Ref Header Row (Default is 1)", min_value=1, value=1) - 1
            df_ref = pd.read_excel(ref_file, sheet_name=ref_sheet, header=ref_header)
            df_ref.columns = [str(c).strip() for c in df_ref.columns]

            # Bind လုပ်မည့် Column ရွေးချယ်ခြင်း
            col_a, col_b = st.columns(2)
            with col_a:
                key_main = st.selectbox("Main Table Key (Code)", working_df.columns)
                amt_main = st.selectbox("Main Table Amount", working_df.columns, index=len(working_df.columns)-1)
            with col_b:
                key_ref = st.selectbox("Ref Table Key (Code)", df_ref.columns)
                amt_ref = st.selectbox("Ref Table Amount", df_ref.columns)

            # --- STEP 3: EXECUTE BINDING ---
            if st.button("🚀 Bind & Compare Now"):
                try:
                    # ✅ Data Type Fix: ID တွေကို String ပြောင်းမှ Error မတက်မှာပါ
                    working_df[key_main] = working_df[key_main].astype(str).str.strip()
                    df_ref[key_ref] = df_ref[key_ref].astype(str).str.strip()
                    
                    # Merge Logic (VLOOKUP)
                    final_bind = pd.merge(working_df, df_ref, left_on=key_main, right_on=key_ref, how='outer', indicator=True)
                    
                    # Difference Calculation
                    final_bind['Variance'] = pd.to_numeric(final_bind[amt_main], errors='coerce').fillna(0) - \
                                             pd.to_numeric(final_bind[amt_ref], errors='coerce').fillna(0)

                    # Display Tabs
                    t1, t2, t3 = st.tabs(["📊 Audit Result", "🔍 Exceptions", "📥 Export"])

                    with t1:
                        st.dataframe(final_bind)

                    with t2:
                        # ပမာဏ မတူတာတွေကို အနီရောင်နဲ့ ပြမယ်
                        diff_amt = final_bind[(final_bind['_merge'] == 'both') & (final_bind['Variance'] != 0)]
                        if not diff_amt.empty:
                            st.error(f"Amount Difference: {len(diff_amt)} items found!")
                            st.dataframe(diff_amt)
                        
                        # တစ်ဖက်တည်းမှာပဲ ရှိတာတွေ
                        missing = final_bind[final_bind['_merge'] != 'both']
                        st.warning(f"Unmatched Items: {len(missing)}")
                        st.dataframe(missing)

                    with t3:
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            final_bind.to_excel(writer, sheet_name='Audit_Report', index=False)
                        
                        st.download_button("Download Final Working Paper", output.getvalue(), "Final_Audit_Report.xlsx")

                except Exception as e:
                    st.error(f"An error occurred: {e}")
