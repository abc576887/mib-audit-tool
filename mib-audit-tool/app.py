import streamlit as st
import pandas as pd
import io

# --- Page Settings ---
st.set_page_config(page_title="Audit Pro - Myanmar", layout="wide")

# Myanmar Unicode Font Support
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pyidaungsu:wght@400;700&display=swap');
    body, div, span, h1, h2, h3, p, th, td { font-family: 'Pyidaungsu', sans-serif !important; }
    .main { background-color: #f8f9fa; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Enterprise Audit & Reconciliation System")
st.markdown("---")

# --- Multi-format File Loader ---
def load_excel_sheets(file):
    try:
        if file.name.endswith('.xlsb'):
            return pd.ExcelFile(file, engine='pyxlsb')
        else:
            return pd.ExcelFile(file)
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# --- Sidebar Configuration ---
st.sidebar.header("⚙️ Settings")
file_a = st.sidebar.file_uploader("Source File (File A)", type=['xlsx', 'xls', 'xlsb'])
file_b = st.sidebar.file_uploader("Target File (File B)", type=['xlsx', 'xls', 'xlsb'])

if file_a and file_b:
    excel_a = load_excel_sheets(file_a)
    excel_b = load_excel_sheets(file_b)
    
    # နှစ်ဖိုင်လုံးမှာ တူတဲ့ Sheet နာမည်တွေကို ယူမယ်
    common_sheets = list(set(excel_a.sheet_names) & set(excel_b.sheet_names))
    
    if not common_sheets:
        st.error("❌ Sheet နာမည်တူ တစ်ခုမှ မတွေ့ပါ။")
    else:
        selected_sheets = st.multiselect("စစ်ဆေးမည့် Sheet များ ရွေးချယ်ပါ", common_sheets, default=common_sheets)
        
        # Unique Key ရွေးရန် (ပထမ Sheet ကနေ Column နာမည်တွေ ယူပြမယ်)
        sample_df = pd.read_excel(file_a, sheet_name=selected_sheets[0])
        key_col = st.selectbox("အဓိက တိုက်စစ်မည့် Column (Unique Key) ကိုရွေးပါ (ဥပမာ - Voucher No, ID)", sample_df.columns)

        if st.button("🚀 စတင်တိုက်စစ်မည်"):
            output = io.BytesIO()
            # Excel Report ထုတ်ဖို့ Writer အဆင်သင့်လုပ်ထားမယ်
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                
                for sheet in selected_sheets:
                    st.write(f"### 📋 Sheet: {sheet}")
                    
                    df_a = pd.read_excel(file_a, sheet_name=sheet)
                    df_b = pd.read_excel(file_b, sheet_name=sheet)

                    # 1. Missing Rows (ဘယ်ဖိုင်မှာ ဘာတွေ လိုနေလဲ)
                    missing_in_b = df_a[~df_a[key_col].isin(df_b[key_col])]
                    missing_in_a = df_b[~df_b[key_col].isin(df_a[key_col])]

                    # 2. Value Mismatch (ID တူပေမယ့် ကျန်တာ ကွဲနေတာ)
                    common_ids = set(df_a[key_col]) & set(df_b[key_col])
                    temp_a = df_a[df_a[key_col].isin(common_ids)].set_index(key_col)
                    temp_b = df_b[df_b[key_col].isin(common_ids)].set_index(key_col)
                    
                    common_cols = list(set(temp_a.columns) & set(temp_b.columns))
                    diff_mask = (temp_a[common_cols] != temp_b[common_cols]).any(axis=1)
                    mismatches = temp_a.loc[diff_mask, common_cols].copy()
                    
                    # Display Results in Tabs
                    tab1, tab2, tab3 = st.tabs(["Missing in B", "Missing in A", "Value Mismatches"])
                    
                    with tab1:
                        st.dataframe(missing_in_b)
                        if not missing_in_b.empty:
                            missing_in_b.to_excel(writer, sheet_name=f"{sheet}_Missing_in_B", index=False)
                    
                    with tab2:
                        st.dataframe(missing_in_a)
                        if not missing_in_a.empty:
                            missing_in_a.to_excel(writer, sheet_name=f"{sheet}_Missing_in_A", index=False)
                            
                    with tab3:
                        st.dataframe(mismatches)
                        if not mismatches.empty:
                            mismatches.to_excel(writer, sheet_name=f"{sheet}_Mismatches")

                    st.markdown("---")
            
            # Download Button
            st.success("✅ စစ်ဆေးခြင်း ပြီးဆုံးပါပြီ။")
            st.download_button(
                label="📥 Download Audit Report (Excel)",
                data=output.getvalue(),
                file_name="Audit_Findings_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

else:
    st.warning("👈 ဆက်လက်ဆောင်ရွက်ရန် ဘယ်ဘက် Sidebar မှ ဖိုင်နှစ်ခုလုံးကို Upload တင်ပေးပါ။")
