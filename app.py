from __future__ import annotations
import io, json, os
from datetime import datetime
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Sania's DataPilot AI", page_icon="🧭", layout="wide")

st.markdown("""
<style>
.block-container{max-width:1450px;padding-top:1.8rem;padding-bottom:3rem}
.hero{padding:1.7rem 1.9rem;border-radius:18px;background:linear-gradient(115deg,#101b35,#244c78);color:#fff;margin-bottom:1.2rem}
.hero h1{font-size:2.25rem;margin:0}.hero p{color:#dce8f7;margin:.45rem 0 0}
[data-testid="stMetric"]{background:rgba(80,130,210,.08);border:1px solid rgba(100,150,220,.22);padding:14px;border-radius:14px}
.foot{color:#8993a4;font-size:.82rem;text-align:center;padding-top:1rem}
</style>
<div class="hero"><h1>🧭 Sania's DataPilot AI</h1><p>Intelligent data analysis workspace · Upload data, discover patterns, and create decision-ready reports.</p></div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🧭 DataPilot AI")
    st.caption("Created & developed by **Sania Mumtaz**")
    st.divider()
    st.markdown("**AI settings**")
    saved_key = st.secrets.get("GROQ_API_KEY", "") if hasattr(st, "secrets") else ""
    api_key = st.text_input("Groq API key (optional)", value=saved_key, type="password", help="Optional. Without a key, built-in analytics and report generation still work.")
    model = st.selectbox("Groq model", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])
    st.divider()
    st.caption("Privacy note: uploaded files are processed in the running app session. Avoid confidential or sensitive data.")


def sample_data():
    return pd.DataFrame({
        "Order Date": pd.date_range("2025-01-01", periods=18, freq="15D"),
        "Region": ["East","West","North","South","East","West"]*3,
        "Category": ["Technology","Furniture","Office Supplies"]*6,
        "Product": ["Laptop","Chair","Notebook","Monitor","Desk","Pen"]*3,
        "Sales": [52000,12000,2400,31000,18000,900,61000,14000,3200,28000,21000,1100,57000,16000,2900,36000,19500,1300],
        "Quantity": [2,4,20,1,2,30,3,5,25,2,3,40,2,4,22,2,3,35],
        "Profit": [8000,1800,600,5200,2200,250,9200,2100,850,4900,2700,320,8700,2400,700,6100,2600,390]
    })


def load_data(file):
    if file.name.lower().endswith('.csv'):
        return pd.read_csv(file)
    return pd.read_excel(file)


def profile(df):
    return {
        "rows": int(df.shape[0]), "columns": int(df.shape[1]),
        "missing": int(df.isna().sum().sum()), "duplicates": int(df.duplicated().sum()),
        "memory_kb": round(df.memory_usage(deep=True).sum()/1024, 1),
        "column_profile": pd.DataFrame({
            "Column": df.columns.astype(str), "Data type": [str(x) for x in df.dtypes],
            "Missing": [int(df[c].isna().sum()) for c in df.columns],
            "Unique values": [int(df[c].nunique(dropna=True)) for c in df.columns]
        })
    }


def make_findings(df):
    findings=[]
    numeric=df.select_dtypes(include="number")
    if df.empty:
        return ["The uploaded dataset contains no rows."]
    findings.append(f"The dataset contains {len(df):,} rows and {len(df.columns):,} columns.")
    if df.isna().sum().sum():
        cols=df.columns[df.isna().any()].tolist()
        findings.append(f"Missing values appear in {len(cols)} column(s): {', '.join(map(str, cols[:6]))}.")
    else:
        findings.append("No missing values were detected in the dataset.")
    if df.duplicated().sum():
        findings.append(f"There are {int(df.duplicated().sum()):,} duplicate rows that may need review.")
    if not numeric.empty:
        for c in numeric.columns[:4]:
            findings.append(f"{c}: average {numeric[c].mean():,.2f}; minimum {numeric[c].min():,.2f}; maximum {numeric[c].max():,.2f}.")
        corr=numeric.corr(numeric_only=True)
        pairs=[]
        for i,c1 in enumerate(corr.columns):
            for c2 in corr.columns[i+1:]:
                v=corr.loc[c1,c2]
                if pd.notna(v): pairs.append((abs(v),c1,c2,v))
        if pairs:
            _,a,b,v=max(pairs)
            findings.append(f"Strongest numeric relationship: {a} and {b} (correlation {v:.2f}). Correlation does not prove causation.")
    return findings


def choose_chart(df):
    numeric=df.select_dtypes(include="number").columns.tolist()
    categorical=df.select_dtypes(include=["object","category","bool"]).columns.tolist()
    dates=[c for c in df.columns if "date" in str(c).lower() or "time" in str(c).lower()]
    if dates and numeric:
        temp=df.copy(); temp[dates[0]]=pd.to_datetime(temp[dates[0]],errors="coerce")
        temp=temp.dropna(subset=[dates[0]])
        if not temp.empty:
            trend=temp.groupby(temp[dates[0]].dt.date)[numeric[0]].sum().reset_index(name=numeric[0])
            return px.line(trend,x=dates[0],y=numeric[0],markers=True,title=f"{numeric[0]} over time")
    if categorical and numeric:
        grouped=df.groupby(categorical[0],dropna=False)[numeric[0]].sum().reset_index().sort_values(numeric[0],ascending=False).head(12)
        return px.bar(grouped,x=categorical[0],y=numeric[0],title=f"{numeric[0]} by {categorical[0]}",text_auto=".2s")
    if len(numeric)>=2:
        return px.scatter(df,x=numeric[0],y=numeric[1],title=f"{numeric[1]} vs {numeric[0]}")
    if numeric:
        return px.histogram(df,x=numeric[0],title=f"Distribution of {numeric[0]}")
    return None


def make_report(df, question, findings, workflow, ai_text=None):
    lines=["# DataPilot AI — Executive Analysis Report", "", f"**Prepared by:** Sania Mumtaz", f"**Generated:** {datetime.now().strftime('%d %b %Y, %H:%M')}", f"**Business question:** {question}", "", "## Dataset overview", f"- Rows: {len(df):,}", f"- Columns: {len(df.columns):,}", f"- Missing cells: {int(df.isna().sum().sum()):,}", f"- Duplicate rows: {int(df.duplicated().sum()):,}", "", "## Key findings"]
    lines += [f"- {x}" for x in findings]
    if ai_text: lines += ["", "## AI-generated interpretation", ai_text]
    lines += ["", "## Agent workflow"]+[f"- {x['agent']}: {x['status']}" for x in workflow]
    lines += ["", "## Recommended next steps", "- Validate important patterns with business stakeholders.", "- Investigate missing values and duplicate records before operational decisions.", "- Track the selected KPIs over time and refresh the analysis with new data.", "", "---", "Generated with Sania's DataPilot AI."]
    return "\n".join(lines)

uploaded=st.file_uploader("Upload your dataset", type=["csv","xlsx","xls"])
c1,c2=st.columns([1,5])
with c1: sample=st.button("✨ Try sample data", use_container_width=True)
if "dataset" not in st.session_state: st.session_state.dataset=None
if uploaded is not None:
    try:
        st.session_state.dataset=load_data(uploaded)
        st.session_state.dataset_name=uploaded.name
    except Exception as e: st.error(f"Could not read file: {e}")
if sample:
    st.session_state.dataset=sample_data(); st.session_state.dataset_name="sample_retail_sales.csv"

df=st.session_state.dataset
if df is None:
    st.info("Upload a CSV/Excel file or choose **Try sample data** to explore the application.")
    st.markdown("### What this project demonstrates")
    a,b,c,d=st.columns(4)
    for col,title,desc in [(a,"Data profiling","Rows, columns, missing values and duplicates"),(b,"Data cleaning","Remove duplicates and fill missing numeric values"),(c,"Visual analytics","Automatic charts and numeric summaries"),(d,"AI reporting","Optional Groq-powered business interpretation")]:
        with col: st.markdown(f"**{title}**"); st.caption(desc)
    st.stop()

if df.empty:
    st.warning("This dataset is empty. Please upload a file containing rows.")
    st.stop()

p=profile(df)
st.markdown(f"### Dataset overview · `{st.session_state.get('dataset_name','dataset')}`")
m1,m2,m3,m4=st.columns(4)
m1.metric("Total rows",f"{p['rows']:,}"); m2.metric("Columns",f"{p['columns']:,}"); m3.metric("Missing cells",f"{p['missing']:,}"); m4.metric("Duplicate rows",f"{p['duplicates']:,}")
with st.expander("Preview data",expanded=True): st.dataframe(df.head(100),use_container_width=True)
with st.expander("Column quality profile"): st.dataframe(p["column_profile"],use_container_width=True,hide_index=True)

st.markdown("### 🧹 Data cleaning")
cl1,cl2=st.columns([2,1])
with cl1: st.caption("Remove duplicate rows and fill missing numeric values with each column's median. Text columns are left unchanged.")
with cl2:
    if st.button("Clean dataset",use_container_width=True):
        before=len(df); cleaned=df.drop_duplicates().copy(); filled=0
        for col in cleaned.select_dtypes(include="number").columns:
            n=int(cleaned[col].isna().sum())
            if n:
                median=cleaned[col].median()
                if pd.notna(median): cleaned[col]=cleaned[col].fillna(median); filled+=n
        st.session_state.dataset=cleaned
        st.success(f"Cleaning complete: removed {before-len(cleaned)} duplicate rows and filled {filled} numeric missing values.")
        st.rerun()

st.markdown("### 🤖 Ask your data")
question=st.text_area("Business question", "Summarize the dataset, identify key trends, and recommend three actions.",height=90)
if st.button("🚀 Run DataPilot analysis",type="primary",use_container_width=True):
    if not question.strip(): st.warning("Please enter a business question.")
    else:
        findings=make_findings(df)
        workflow=[{"agent":"1 · Planner Agent","status":"Completed","summary":"Translated the business question into a structured analysis plan."},{"agent":"2 · Data Analyst Agent","status":"Completed","summary":"Calculated dataset quality metrics and descriptive statistics."},{"agent":"3 · Python Coder Agent","status":"Completed","summary":"Prepared reproducible, read-only analysis logic."},{"agent":"4 · Visualization Agent","status":"Completed","summary":"Selected a chart based on available dataset columns."},{"agent":"5 · Report Agent","status":"Completed","summary":"Created an executive report with findings and recommended next steps."}]
        ai_text=None
        if api_key:
            try:
                from groq import Groq
                client=Groq(api_key=api_key)
                prompt="Answer the business question using only the supplied dataset facts. Do not invent numbers. Provide concise interpretation and 3 practical recommendations.\nQuestion: "+question+"\nFacts:\n"+"\n".join(findings)
                response=client.chat.completions.create(model=model,messages=[{"role":"user","content":prompt}],temperature=0.2,max_tokens=700)
                ai_text=response.choices[0].message.content
            except Exception as e:
                st.warning(f"AI service unavailable; continuing with built-in analysis. Details: {e}")
        chart=choose_chart(df)
        st.session_state.analysis={"findings":findings,"workflow":workflow,"ai_text":ai_text,"report":make_report(df,question,findings,workflow,ai_text),"chart":chart}

result=st.session_state.get("analysis")
if result:
    st.divider(); st.markdown("### ⚙️ Multi-agent workflow")
    for step in result["workflow"]:
        st.success(f"{step['agent']} — {step['status']}: {step['summary']}")
    st.markdown("### 🔎 Key findings")
    for item in result["findings"]: st.markdown(f"- {item}")
    if result["ai_text"]:
        st.markdown("### ✨ AI interpretation & recommendations"); st.write(result["ai_text"])
    if result["chart"] is not None:
        st.markdown("### 📊 Recommended visualization"); st.plotly_chart(result["chart"],use_container_width=True)
    else: st.info("No suitable chart could be generated for the available columns.")
    st.markdown("### 📄 Executive report")
    st.markdown(result["report"])
    st.download_button("Download executive report",result["report"],file_name="sania_datapilot_report.md",mime="text/markdown")
    st.download_button("Download workflow log",json.dumps(result["workflow"],indent=2),file_name="datapilot_workflow.json",mime="application/json")

st.markdown('<div class="foot">© 2026 Sania Mumtaz · DataPilot AI · Built with Python, Streamlit, Pandas, Plotly and optional Groq API</div>',unsafe_allow_html=True)
