import streamlit as st
import pandas as pd

# --- Page Config ---
st.set_page_config(page_title="Dynamic Audit Tool", layout="wide")

# မြန်မာစာအတွက် CSS (Optional - standard streamlit support unicode)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pyidaungsu&display=swap');
    html, body, [class*="css"]  { font-family: 'Pyidaungsu', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Universal Audit Tool (Dynamic Column Support)")

# --- Sidebar ---
st.sidebar.header("Navigation")
menu = st.sidebar.radio("Audit Module ရွေးချယ်ပါ", 
    ["💰 Finance/Banking", "📦 Inventory", "🏭 Production"])

# --- Flexible Data Loader ---
def load_data(file):
    try:
        if file.name.endswith('.csv'):
            return pd.read_csv(file)
        elif file.name.endswith('.xlsb'):
            return pd.read_excel(file, engine='pyxlsb')
        else:
            return pd.read_excel(file) # For .xlsx and .xls
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

# --- Main Logic ---
uploaded_file = st.file_uploader("Excel သို့မဟုတ် CSV ဖိုင် တင်ပေးပါ", type=['csv', 'xlsx', 'xls', 'xlsb'])

if uploaded_file:
    df = load_data(uploaded_file)
    
    if df is not None:
        # Heading တွေအားလုံးကို List အနေနဲ့ ယူမယ်
        all_columns = df.columns.tolist()
        
        st.success("File Upload အောင်မြင်ပါသည်။")
        st.write("### Data Preview (ပထမ ၅ ကြောင်း)")
        st.dataframe(df.head())

        # --- Finance Module ---
        if menu == "💰 Finance/Banking":
            st.subheader("Finance Audit Logic")
            
            col1, col2 = st.columns(2)
            with col1:
                # Column နာမည်ကို အသေမယူဘဲ User ကို ရွေးခိုင်းမယ်
                amount_col = st.selectbox("ငွေပမာဏ Column ကို ရွေးပါ (Amount)", all_columns)
                date_col = st.selectbox("ရက်စွဲ Column ကို ရွေးပါ (Date)", all_columns)
            
            with col2:
                threshold = st.number_input("စစ်ဆေးလိုသည့် အနည်းဆုံး ပမာဏ (Threshold)", value=100000)

            # Calculation
            high_values = df[df[amount_col] >= threshold]
            st.warning(f"သတ်မှတ်ချက်ထက်ကျော်သော စာရင်းပေါင်း: {len(high_values)}")
            st.dataframe(high_values)

        # --- Inventory Module ---
        elif menu == "📦 Inventory":
            st.subheader("Inventory Audit Logic")
            
            stock_col = st.selectbox("လက်ကျန်အရေအတွက် Column ကို ရွေးပါ (Quantity)", all_columns)
            
            # Negative Stock Check
            neg_stock = df[df[stock_col] < 0]
            if not neg_stock.empty:
                st.error(f"လက်ကျန်အနှုတ်ပြနေသော စာရင်း {len(neg_stock)} ခု တွေ့ရှိပါသည်။")
                st.dataframe(neg_stock)
            else:
                st.balloons()
                st.success("လက်ကျန်အနှုတ်စာရင်း မရှိပါ။")

        # --- Production Module ---
        elif menu == "🏭 Production":
            st.subheader("Production & Principal Reconciliation")
            
            join_col = st.selectbox("နှိုင်းယှဉ်မည့် Key Column ကိုရွေးပါ (ဥပမာ - SKU သို့မဟုတ် ID)", all_columns)
            val_col = st.selectbox("စစ်ဆေးမည့် Value Column (ဥပမာ - Production Qty)", all_columns)
            
            # ဤနေရာတွင် ဒုတိယဖိုင်နှင့် ချိတ်ဆက်ခြင်း သို့မဟုတ် Target နှင့် နှိုင်းယှဉ်ခြင်း လုပ်နိုင်သည်
            st.info(f"{join_col} အပေါ် အခြေခံ၍ {val_col} ကို စစ်ဆေးရန် အဆင်သင့်ဖြစ်ပါပြီ။")

# --- Libraries Install လုပ်ရန် လိုအပ်ချက် ---
# pip install streamlit pandas openpyxl pyxlsb
