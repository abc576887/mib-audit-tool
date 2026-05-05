import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="SGF Triple Audit System", layout="wide")

st.title("🛡️ SGF Advanced Triple-File Auditor")
st.info("ဖိုင် (၃) ဖိုင်လုံးကို Upload တင်ပြီး Sheet အလိုက် တိုက်စစ်နိုင်ပါသည်။")

# --- Sidebar & File Uploaders ---
st.sidebar.header("📂 Upload Files")
f1 = st.sidebar.file_uploader("File 1: SGF Raw (1-2025)_2.xlsx", type=['xlsx', 'xlsb'])
f2 = st.sidebar.file_uploader("File 2: SGF Raw (2-2025).xlsx", type=['xlsx', 'xlsb'])
f3 = st.sidebar.file_uploader("File 3: 1_MDY SGD Cash (1-2025).xlsx", type=['xlsx', 'xlsb'])

# Config Settings
st.sidebar.divider()
skip_r = st.sidebar.number_input("Heading အပေါ်က Row များကို ကျော်ဖတ်ရန် (Skip Rows)", min_value=0, value=0)

if f1 and f2 and f3:
    # Read Excel Files
    xls1 = pd.ExcelFile(f1)
    xls2 = pd.ExcelFile(f2)
    xls3 = pd.ExcelFile(f3)

    # ဘုံတူညီသော Sheet များကို ရှာဖွေခြင်း
    common_sheets = list(set(xls1.sheet_names) & set(xls2.sheet_names) & set(xls3.sheet_names))
    
    if not common_sheets:
        # Sheet နာမည်မတူရင် User ကို ကိုယ်တိုင်ရွေးခိုင်းမယ်
        st.warning("⚠️ ဖိုင်သုံးခုလုံးတွင် Sheet နာမည်တူ မရှိပါ။ တစ်ခုချင်းစီ ရွေးချယ်ပေးပါ။")
        col1, col2, col3 = st.columns(3)
        with col1: s1 = st.selectbox("Sheet from File 1", xls1.sheet_names)
        with col2: s2 = st.selectbox("Sheet from File 2", xls2.sheet_names)
        with col3: s3 = st.selectbox("Sheet from File 3", xls3.sheet_names)
        process_list = [(s1, s2, s3)]
    else:
        selected = st.multiselect("တိုက်စစ်မည့် Sheet များကို ရွေးပါ", common_sheets, default=common_sheets)
        process_list = [(s, s, s) for s in selected]

    # Unique Key Selection (ပထမဖိုင်ရဲ့ ပထမ Sheet ကို နမူနာယူမယ်)
    sample_df = pd.read_excel(f1, sheet_name=xls1.sheet_names[0], skiprows=skip_r)
    key_col = st.selectbox("တိုက်စစ်မည့် အဓိက Heading (Unique Key) ကိုရွေးပါ", sample_df.columns)

    if st.button("🚀 Triple Reconciliation စတင်မည်"):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            
            for s1, s2, s3 in process_list:
                st.subheader(f"📊 Analyzing: {s1} | {s2} | {s3}")
                
                # Load Data
                df1 = pd.read_excel(f1, sheet_name=s1, skiprows=skip_r)
                df2 = pd.read_excel(f2, sheet_name=s2, skiprows=skip_r)
                df3 = pd.read_excel(f3, sheet_name=s3, skiprows=skip_r)

                # Column Cleaning
                for df in [df1, df2, df3]:
                    df.columns = df.columns.str.strip()
                    # Remove Unnamed columns
                    df.drop(columns=[c for c in df.columns if 'Unnamed' in str(c)], inplace=True)

                # --- Comparison Logic ---
                # 1. ၃ ဖိုင်လုံးမှာ ပါတဲ့ Key များကို ရှာခြင်း
                ids1, ids2, ids3 = set(df1[key_col]), set(df2[key_col]), set(df3[key_col])
                
                all_keys = ids1 | ids2 | ids3
                summary_data = []
                
                for k in all_keys:
                    in_f1 = "✅" if k in ids1 else "❌"
                    in_f2 = "✅" if k in ids2 else "❌"
                    in_f3 = "✅" if k in ids3 else "❌"
                    summary_data.append({key_col: k, "File 1": in_f1, "File 2": in_f2, "File 3": in_f3})
                
                summary_df = pd.DataFrame(summary_data)
                
                # Filter out only discrepancies (အကုန်လုံး ✅ မဟုတ်တာတွေကိုပဲ ပြမယ်)
                issues = summary_df[(summary_df["File 1"] == "❌") | (summary_df["File 2"] == "❌") | (summary_df["File 3"] == "❌")]

                # Display Result
                st.write(f"တွေ့ရှိချက် အကျဉ်းချုပ် (Issues: {len(issues)})")
                st.dataframe(issues)
                
                # Save to Excel Report
                issues.to_excel(writer, sheet_name=f"Audit_{s1[:25]}", index=False)
                st.divider()

        st.success("✅ Audit ပြီးဆုံးပါပြီ။")
        st.download_button("📥 Download 3-File Audit Report", output.getvalue(), "Triple_Audit_Report.xlsx")

else:
    st.warning("👈 ကျေးဇူးပြု၍ ဘယ်ဘက်မှ ဖိုင် (၃) ဖိုင်လုံးကို Upload တင်ပေးပါ။")
