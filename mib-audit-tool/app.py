import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

# --- Page Config ---
st.set_page_config(page_title="SGF Audit System", layout="wide")

def clean_df(df):
    """Excel မှ Data များကို Clean လုပ်ရန် (Space ဖယ်ခြင်း နှင့် Numeric ပြောင်းခြင်း)"""
    df.columns = [str(c).strip() for c in df.columns]
    # စာရင်းအင်း Column များကို ကိန်းဂဏန်းပြောင်း (စာသားပါရင် 0 ထား)
    numeric_cols = ['Opening', 'Purchase', 'Surplus', 'Tansfer In', 'Other In', 'Total Received', 'Total Usage', 'Closing']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

st.title("🍵 Shan Gyee Factory - Audit Automation Tool")
st.info("Excel File တင်ပြီး Sheet တစ်ခုနှင့်တစ်ခု (သို့မဟုတ်) Formula များ တိုက်စစ်နိုင်ပါသည်။")

# --- File Upload ---
uploaded_file = st.sidebar.file_uploader("SGF Raw Excel File ကို ရွေးပါ", type=["xlsx"])

if uploaded_file:
    xl = pd.ExcelFile(uploaded_file)
    sheets = xl.sheet_names
    
    tab1, tab2 = st.tabs(["📊 Formula Audit (Internal)", "🔄 Cross-Sheet Audit (Carry Forward)"])

    # --- TAB 1: Internal Logic Audit (Row အလိုက် စစ်ဆေးခြင်း) ---
    with tab1:
        st.subheader("Sheet တစ်ခုအတွင်းရှိ အတွက်အချက်များ စစ်ဆေးခြင်း")
        selected_sheet = st.selectbox("Audit လုပ်မည့် Sheet ကိုရွေးပါ", sheets, key="internal")
        
        # Row 3 မှ စဖတ်မည် (Heading ကျော်ရန်)
        df = pd.read_excel(uploaded_file, sheet_name=selected_sheet, skiprows=3)
        df = clean_df(df)
        
        if 'Total Received' in df.columns:
            # Audit Logic: Opening + Purchase + Surplus + Transfer In + Other In = Total Received
            df['Calculated_Received'] = df['Opening'] + df['Purchase'] + df['Surplus'] + df['Tansfer In'] + df['Other In']
            df['Rec_Diff'] = df['Calculated_Received'] - df['Total Received']
            
            # Closing Check: Total Received - Total Usage = Closing (သင့် Formula အတိုင်း ပြင်နိုင်သည်)
            if 'Total Usage' in df.columns and 'Closing' in df.columns:
                df['Calculated_Closing'] = df['Total Received'] - df['Total Usage']
                df['Close_Diff'] = df['Calculated_Closing'] - df['Closing']

            # Difference ရှိသော Row များကိုသာ ပြမည်
            diff_mask = (df['Rec_Diff'].abs() > 0.01) | (df.get('Close_Diff', 0).astype(float).abs() > 0.01)
            errors = df[diff_mask]

            if not errors.empty:
                st.error(f"⚠️ ကွာဟချက်ရှိသော Row ပေါင်း {len(errors)} ခု တွေ့ရှိရသည်။")
                st.dataframe(errors)
            else:
                st.success("✅ ဤ Sheet အတွင်းရှိ Formula များအားလုံး ကိုက်ညီမှုရှိပါသည်။")

    # --- TAB 2: Cross-Sheet Audit (လွန်ခဲ့သောလ Closing နှင့် ယခုလ Opening တိုက်စစ်ခြင်း) ---
    with tab2:
        st.subheader("Sheet အချင်းချင်း တိုက်စစ်ခြင်း (Carry Forward)")
        c1, c2 = st.columns(2)
        with c1:
            prev_s = st.selectbox("ယခင် Sheet (Closing ယူရန်)", sheets, key="prev")
        with c2:
            curr_s = st.selectbox("ယခု Sheet (Opening တိုက်ရန်)", sheets, key="curr")

        if st.button("Cross-Check Run မည်"):
            df_p = clean_df(pd.read_excel(uploaded_file, sheet_name=prev_s, skiprows=3))
            df_c = clean_df(pd.read_excel(uploaded_file, sheet_name=curr_s, skiprows=3))

            # Code ကို အခြေခံပြီး Bind လုပ်မည်
            merged = pd.merge(
                df_p[['Code', 'Description', 'Closing']], 
                df_c[['Code', 'Opening']], 
                on='Code', 
                how='outer', 
                suffixes=('_OldSheet', '_NewSheet')
            )

            merged['Carry_Diff'] = merged['Closing'].fillna(0) - merged['Opening'].fillna(0)
            cross_errors = merged[merged['Carry_Diff'].abs() > 0.01]

            if not cross_errors.empty:
                st.warning("❌ Closing နှင့် Opening မကိုက်ညီသော စာရင်းများ")
                st.dataframe(cross_errors)
                
                # Export Result
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    cross_errors.to_excel(writer, index=False, sheet_name='Audit_Difference')
                
                st.download_button(
                    label="Difference Report ကို Excel ဖြင့် ဒေါင်းလုဒ်ဆွဲရန်",
                    data=output.getvalue(),
                    file_name="Audit_Difference_Report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.success("🎉 Sheet နှစ်ခုကြား စာရင်းများ ကိုက်ညီမှုရှိပါသည်။")

else:
    st.write("👈 ဘယ်ဘက် Sidebar တွင် Excel File ကို အရင် တင်ပေးပါ။")
