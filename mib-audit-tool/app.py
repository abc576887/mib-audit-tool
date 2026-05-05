import streamlit as st
import pandas as pd
import io

# Page Config
st.set_config(page_title="AuditLink Pro - MM", layout="wide")

st.title("🔍 စမတ်ကျသော စာရင်းစစ်နှင့် တိုက်စစ်စနစ် (Audit & Recon)")
st.info("💡 Excel Version အားလုံးနှင့် မြန်မာစာ (Unicode/Zawgyi) ကို အထောက်အပံ့ပေးပါသည်။")

# ၁။ File Upload Section (xls, xlsx, csv အားလုံးရသည်)
col1, col2 = st.columns(2)
with col1:
    main_file = st.file_uploader("ပင်မဖိုင် (Main Ledger)", type=['xlsx', 'xls', 'csv'])
with col2:
    ref_file = st.file_uploader("တိုက်စစ်မည့်ဖိုင် (Bank/Statement)", type=['xlsx', 'xls', 'csv'])

def load_data(file):
    if file is not None:
        if file.name.endswith('.csv'):
            # မြန်မာစာအတွက် encoding ကို utf-8-sig သုံးထားသည်
            return pd.read_csv(file, encoding='utf-8-sig')
        else:
            # Excel version အားလုံးအတွက် engine=None က auto detect လုပ်ပေးသည်
            return pd.read_excel(file)
    return None

df_main = load_data(main_file)
df_ref = load_data(ref_file)

if df_main is not None and df_ref is not None:
    st.markdown("---")
    st.subheader("⚙️ တိုက်စစ်မည့် ကော်လံများ ရွေးချယ်ပါ")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        key_main = st.selectbox("Main Key (ID/Voucher)", df_main.columns)
    with c2:
        key_ref = st.selectbox("Ref Key (ID/Voucher)", df_ref.columns)
    with c3:
        amt_main = st.selectbox("Amount (Main)", df_main.columns)
    with c4:
        amt_ref = st.selectbox("Amount (Ref)", df_ref.columns)

    if st.button("စစ်ဆေးမှု စတင်မည်"):
        # Data Cleaning: မြန်မာစာကြားထဲက Space တွေနဲ့ ID တွေကို ရှင်းလင်းခြင်း
        df_main[key_main] = df_main[key_main].astype(str).str.strip()
        df_ref[key_ref] = df_ref[key_ref].astype(str).str.strip()

        # Logic: XLOOKUP Style Bidirectional Match
        # 
        result = pd.merge(df_main, df_ref, left_on=key_main, right_on=key_ref, how='outer', indicator=True)
        
        # တွက်ချက်မှုများ
        result['Variance'] = result[amt_main].fillna(0) - result[amt_ref].fillna(0)

        # Tab အလိုက် ရလဒ်များပြသခြင်း
        tab1, tab2, tab3 = st.tabs(["📊 အကျဉ်းချုပ်", "❌ ကွဲလွဲချက်များ", "👯 ထပ်နေသောစာရင်းများ"])

        with tab1:
            st.write("### စာရင်းစစ်ဆေးမှု အခြေအနေ")
            reconciled = len(result[result['_merge'] == 'both'])
            st.metric("ကိုက်ညီသော အရေအတွက်", f"{reconciled} ခု")
            st.dataframe(result)

        with tab2:
            st.write("### မကိုက်ညီသော စာရင်းများ (Exceptions)")
            # တစ်ဖက်တည်းမှာပဲ ရှိတာတွေနဲ့ ပမာဏ မတူတာတွေကို စုထုတ်ခြင်း
            exceptions = result[(result['_merge'] != 'both') | (result['Variance'] != 0)]
            st.dataframe(exceptions)

        with tab3:
            st.write("### Double Entry (Duplicates) စစ်ဆေးချက်")
            dupes = df_main[df_main.duplicated(subset=[key_main], keep=False)]
            st.dataframe(dupes)

        # Report ထုတ်ခြင်း
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            result.to_excel(writer, sheet_name='Audit_Summary', index=False)
            exceptions.to_excel(writer, sheet_name='Exceptions_Report', index=False)
            
        st.download_button(
            label="📥 Audit Report (Excel) ထုတ်ယူရန်",
            data=output.getvalue(),
            file_name="Audit_Report_Final.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
