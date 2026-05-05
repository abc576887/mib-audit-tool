import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Flexible Audit Tool", layout="wide")

def load_and_clean(file, sheet):
    # Row 3 ကနေ စဖတ်မယ် (Format မတူရင်တောင် Table ခေါင်းစဉ်က အဲဒီနားမှာ ရှိတတ်လို့ပါ)
    df = pd.read_excel(file, sheet_name=sheet, skiprows=3)
    df.columns = [str(c).strip() for c in df.columns]
    # Unnamed column တွေ ဖယ်မယ်
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    return df

st.title("🛡️ SGF Flexible Audit Tool")

uploaded_file = st.sidebar.file_uploader("Excel ဖိုင်တင်ပါ", type=["xlsx"])

if uploaded_file:
    xl = pd.ExcelFile(uploaded_file)
    sheets = xl.sheet_names
    
    st.sidebar.markdown("---")
    selected_sheet = st.sidebar.selectbox("Audit လုပ်မည့် Sheet", sheets)
    
    # Data Loading
    df = load_and_clean(uploaded_file, selected_sheet)
    all_cols = df.columns.tolist()

    st.subheader(f"🔍 Column Matching for: {selected_sheet}")
    st.write("Excel ထဲက Column အမည်တွေ မတူရင်တောင် အောက်မှာ သက်ဆိုင်ရာ Column ကို ရွေးပေးပါ")

    # Column တွေကို User က Manual ချိတ်ပေးရမယ့်အပိုင်း
    col1, col2, col3 = st.columns(3)
    with col1:
        id_col = st.selectbox("Product Code (Key)", all_cols, index=0)
        desc_col = st.selectbox("Description", all_cols, index=1)
    with col2:
        open_col = st.selectbox("Opening Balance", all_cols)
        receive_col = st.selectbox("Total Received", all_cols)
    with col3:
        close_col = st.selectbox("Closing Balance", all_cols)
        usage_col = st.selectbox("Total Usage/Out", all_cols)

    if st.button("📊 စာရင်းတိုက်စစ်မည်"):
        # Numeric ပြောင်းခြင်း
        for c in [open_col, receive_col, close_col, usage_col]:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

        # Audit Logic 1: Opening + Received - Usage = Closing
        df['Calculated_Closing'] = df[open_col] + df[receive_col] - df[usage_col]
        df['Diff'] = df['Calculated_Closing'] - df[close_col]

        # Difference ရှိတာတွေကို စစ်ထုတ်ခြင်း
        error_df = df[df['Diff'].abs() > 0.01].copy()

        if not error_df.empty:
            st.error(f"❌ ကွာဟချက် {len(error_df)} ခု တွေ့ရှိရပါသည်။")
            # လိုအပ်တဲ့ Column တွေကိုပဲ ပြမယ်
            display_cols = [id_col, desc_col, open_col, receive_col, usage_col, close_col, 'Calculated_Closing', 'Diff']
            st.dataframe(error_df[display_cols])
            
            # Export
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                error_df.to_excel(writer, index=False, sheet_name='Audit_Report')
            st.download_button("Download Audit Report", output.getvalue(), "audit_result.xlsx")
        else:
            st.success("✅ စာရင်းများအားလုံး ကိုက်ညီမှုရှိပါသည်။ (Mathematical Consistency OK)")

else:
    st.info("အလုပ်စတင်ရန် ဘယ်ဘက်မှ Excel File ကိုအရင် Upload တင်ပါ။")
