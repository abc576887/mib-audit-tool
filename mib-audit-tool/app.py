import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Myanmar Auditor Tool", layout="wide")

st.title("🔍 Advanced Audit & Reconciliation Tool")
st.write("Excel ဖိုင်များကို XLOOKUP Style ဖြင့် တိုက်စစ်ပြီး Audit လုပ်ရန်")

# --- Sidebar: File Upload ---
st.sidebar.header("Upload Files")
source_file = st.sidebar.file_uploader("စစ်ဆေးမည့်ဖိုင် တင်ပါ (e.g. Cash Book/GL)", type=['xlsx'])
target_file = st.sidebar.file_uploader("အတည်ပြုမည့်ဖိုင် တင်ပါ (e.g. Bank/Master)", type=['xlsx'])

if source_file and target_file:
    df_src = pd.read_excel(source_file)
    df_tgt = pd.read_excel(target_file)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Source Data (Preview)")
        st.dataframe(df_src.head(5))
    with col2:
        st.subheader("Target Data (Preview)")
        st.dataframe(df_tgt.head(5))

    st.divider()

    # --- Audit Configuration ---
    st.header("Audit Configuration")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        join_key = st.selectbox("တိုက်စစ်မည့် Key (ID/Voucher No)", options=df_src.columns)
    with c2:
        src_amt = st.selectbox("Source ပမာဏ Column", options=df_src.columns)
    with c3:
        tgt_amt = st.selectbox("Target ပမာဏ Column", options=df_tgt.columns)

    if st.button("Run Audit Process"):
        # 1. Logic: XLOOKUP Style Merge
        # Outer join သုံးထားလို့ နှစ်ဖက်လုံးက missing data တွေကို မိစေမှာပါ
        merged = pd.merge(df_src, df_tgt, left_on=join_key, right_on=join_key, how='outer', suffixes=('_Source', '_Target'))

        # 2. Calculation
        merged['Variance'] = merged[src_amt].fillna(0) - merged[tgt_amt].fillna(0)

        # 3. Status Tagging
        def get_status(row):
            if pd.isna(row[src_amt]): return "Missing in Source (Book)"
            if pd.isna(row[tgt_amt]): return "Missing in Target (Bank/Physical)"
            if row['Variance'] != 0: return "Amount Discrepancy"
            return "Matched (OK)"

        merged['Audit_Status'] = merged.apply(get_status, axis=1)

        # Display Results
        st.success("Audit လုပ်ဆောင်ချက် ပြီးမြောက်ပါပြီ!")
        
        # Summary Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Rows", len(merged))
        m2.metric("Matched", len(merged[merged['Audit_Status'] == "Matched (OK)"]))
        m3.metric("Discrepancies", len(merged[merged['Audit_Status'] != "Matched (OK)"]))

        st.dataframe(merged)

        # --- Excel Download Button ---
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            merged.to_excel(writer, index=False, sheet_name='Audit_Report')
        
        st.download_button(
            label="Download Full Audit Report (Excel)",
            data=output.getvalue(),
            file_name="audit_report_final.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.info("အပေါ်က Sidebar မှာ Excel ဖိုင်နှစ်ခုကို အရင်တင်ပေးပါ။")