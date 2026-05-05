import streamlit as st
import pandas as pd

# --- Page Config ---
st.set_page_config(page_title="Multi-Sheet Audit Tool", layout="wide")

# --- File Loader Function ---
def get_all_sheets(file):
    try:
        # Excel ဖိုင်ထဲက Sheet နာမည်အားလုံးကို ဖတ်မယ်
        xl = pd.ExcelFile(file)
        return xl.sheet_names
    except Exception as e:
        st.error(f"Error reading sheets: {e}")
        return []

# --- Main App ---
st.title("🛡️ Multi-Sheet Dynamic Audit Tool")

uploaded_file = st.file_uploader("Excel ဖိုင်တင်ပါ", type=['xlsx', 'xls', 'xlsb'])

if uploaded_file:
    # 1. Sheet နာမည်တွေကို အရင်ပြမယ်
    sheet_names = get_all_sheets(uploaded_file)
    
    if sheet_names:
        selected_sheet = st.sidebar.selectbox("စစ်ဆေးမည့် Sheet ကိုရွေးပါ", sheet_names)
        
        # 2. ရွေးချယ်လိုက်တဲ့ Sheet တစ်ခုတည်းကိုပဲ ဖတ်မယ်
        df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
        
        st.success(f"Selected Sheet: {selected_sheet}")
        
        # 3. Column Heading များကို ယူမယ်
        all_columns = df.columns.tolist()
        
        # UI Layout
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Audit Parameters")
            target_col = st.selectbox("စစ်ဆေးမည့် Column (Heading)", all_columns)
            audit_type = st.radio("စစ်ဆေးမည့်ပုံစံ", ["Duplicate Check", "Negative Value", "Blank Cells"])
            
        with col2:
            st.subheader("Result Preview")
            if audit_type == "Duplicate Check":
                results = df[df.duplicated(subset=[target_col], keep=False)]
                st.write(f"ထပ်နေသောစာရင်း: {len(results)}")
                st.dataframe(results)
                
            elif audit_type == "Negative Value":
                # Numeric ဖြစ်မှ စစ်လို့ရအောင် handle လုပ်မယ်
                df[target_col] = pd.to_numeric(df[target_col], errors='coerce')
                results = df[df[target_col] < 0]
                st.write(f"အနှုတ်စာရင်း: {len(results)}")
                st.dataframe(results)

            elif audit_type == "Blank Cells":
                results = df[df[target_col].isna()]
                st.write(f"လွတ်နေသောစာရင်း: {len(results)}")
                st.dataframe(results)
