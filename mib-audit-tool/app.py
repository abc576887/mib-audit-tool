import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
from io import BytesIO

st.set_page_config(page_title="Audit System V2", layout="wide")
st.title("🧠 Internal Audit System V2 (Business Grade)")

# =========================
# DATABASE (Audit History)
# =========================
conn = sqlite3.connect("audit.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT,
    issues INTEGER
)
""")
conn.commit()

# =========================
# HELPER FUNCTIONS
# =========================

def load_excel(file):
    xls = pd.ExcelFile(file)
    return {s: xls.parse(s) for s in xls.sheet_names}

def multi_file_merge(df1, df2, key):
    return df1.merge(df2, on=key, how='left', suffixes=('', '_ref'))

def detect_all(df, col1, col2):
    results = {}

    results['nulls'] = df[df.isnull().any(axis=1)]
    results['duplicates'] = df[df.duplicated()]

    df['diff'] = df[col1] - df[col2]
    results['mismatch'] = df[df['diff'] != 0]

    mean = df[col1].mean()
    std = df[col1].std()
    df['z'] = (df[col1] - mean) / std
    results['outliers'] = df[abs(df['z']) > 3]

    df['fraud_score'] = (
        (df['diff'] != 0).astype(int) +
        (df['z'].abs() > 3).astype(int) +
        (df.duplicated()).astype(int)
    )

    results['scored'] = df
    return results

def apply_rules(df, rules):
    violations = []
    for rule in rules:
        col = rule['column']
        cond = rule['condition']

        if cond == ">0":
            violations.append(df[df[col] <= 0])
        elif cond == ">=0":
            violations.append(df[df[col] < 0])
        elif cond == "not_null":
            violations.append(df[df[col].isnull()])

    if violations:
        return pd.concat(violations)
    return pd.DataFrame()

def export_excel(results):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for k, v in results.items():
            v.to_excel(writer, sheet_name=k[:30], index=False)
    return output.getvalue()

# =========================
# SIDEBAR CONFIG
# =========================

st.sidebar.header("⚙️ Configuration")

file1 = st.sidebar.file_uploader("Upload Main File", type=["xlsx"])
file2 = st.sidebar.file_uploader("Upload Reference File (Optional)", type=["xlsx"])

rules = [
    {"column": "amount", "condition": ">=0"},
    {"column": "qty", "condition": ">0"}
]

# =========================
# MAIN LOGIC
# =========================

if file1:

    sheets1 = load_excel(file1)
    sheet1_name = st.selectbox("Select Sheet (Main)", list(sheets1.keys()))
    df1 = sheets1[sheet1_name]

    st.subheader("📄 Main Data")
    st.dataframe(df1.head())

    if file2:
        sheets2 = load_excel(file2)
        sheet2_name = st.selectbox("Select Sheet (Reference)", list(sheets2.keys()))
        df2 = sheets2[sheet2_name]

        key = st.selectbox("Join Key", df1.columns)

        df = multi_file_merge(df1, df2, key)

        st.subheader("🔗 Merged Data")
        st.dataframe(df.head())
    else:
        df = df1

    col1 = st.selectbox("Column 1 (Compare)", df.columns)
    col2 = st.selectbox("Column 2 (Compare)", df.columns)

    if st.button("🚀 Run Full Audit"):

        results = detect_all(df.copy(), col1, col2)

        # Apply Rule Engine
        rule_violations = apply_rules(df, rules)
        results['rule_violations'] = rule_violations

        total_issues = sum(len(v) for v in results.values())

        # Save Log
        c.execute("INSERT INTO audit_log (filename, issues) VALUES (?, ?)",
                  (file1.name, total_issues))
        conn.commit()

        # =========================
        # DISPLAY
        # =========================
        st.subheader("📊 Audit Results")

        for k, v in results.items():
            st.write(f"### {k} ({len(v)})")
            st.dataframe(v.head(50))

        # =========================
        # BINDER (EXPORT)
        # =========================
        excel = export_excel(results)

        st.download_button(
            "📥 Download Audit Binder",
            data=excel,
            file_name="audit_binder.xlsx"
        )

# =========================
# AUDIT HISTORY
# =========================

st.sidebar.subheader("📜 Audit History")

history = pd.read_sql("SELECT * FROM audit_log ORDER BY id DESC", conn)
st.sidebar.dataframe(history)
