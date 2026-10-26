import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Student Performance Lab", page_icon="🎓", layout="wide")
st.title("🎓 Student Performance Analytics")
st.caption("Mini Project | Big Data Analytics | Prepared for Priya")
st.markdown("Analyze academic results, compare subjects, find toppers, and explore student performance with interactive filters.")

@st.cache_data
def default_data():
    return pd.read_csv("student_performance.csv")

uploaded = st.sidebar.file_uploader("Upload student CSV (optional)", type=["csv"])
try:
    df = pd.read_csv(uploaded) if uploaded else default_data()
except Exception as e:
    st.error(f"Unable to read CSV: {e}")
    st.stop()

subjects = ["Big Data", "Python", "Statistics", "Database", "Machine Learning"]
required = {"Student_ID", "Student_Name", "Class", "Result"} | set(subjects)
if not required.issubset(df.columns):
    st.error("Dataset needs Student_ID, Student_Name, Class, Result and these subject columns: " + ", ".join(subjects))
    st.stop()
for s in subjects:
    df[s] = pd.to_numeric(df[s], errors="coerce")
df["Total_Marks"] = df[subjects].sum(axis=1)
df["Percentage"] = (df["Total_Marks"] / (len(subjects)*100) * 100).round(2)
df["Result"] = df[subjects].ge(35).all(axis=1).map({True:"Pass", False:"Fail"})

st.sidebar.header("Explore students")
classes = sorted(df["Class"].dropna().astype(str).unique())
chosen_classes = st.sidebar.multiselect("Class / course", classes, default=classes)
result_options = ["Pass", "Fail"]
chosen_results = st.sidebar.multiselect("Result", result_options, default=result_options)
filtered = df[df["Class"].astype(str).isin(chosen_classes) & df["Result"].isin(chosen_results)].copy()

total = len(filtered)
pass_count = int((filtered["Result"]=="Pass").sum())
pass_rate = (pass_count/total*100) if total else 0
avg = filtered["Percentage"].mean() if total else 0
topper = filtered.loc[filtered["Percentage"].idxmax(), "Student_Name"] if total else "—"

a,b,c,d = st.columns(4)
a.metric("Students", f"{total:,}")
b.metric("Pass Percentage", f"{pass_rate:.1f}%")
c.metric("Average Score", f"{avg:.1f}%")
d.metric("Top Performer", str(topper))

st.divider()
left,right = st.columns(2)
with left:
    st.subheader("Average Marks by Subject")
    subject_avg = filtered[subjects].mean().rename_axis("Subject").reset_index(name="Average Marks") if total else pd.DataFrame({"Subject":subjects,"Average Marks":[0]*len(subjects)})
    st.plotly_chart(px.bar(subject_avg, x="Subject", y="Average Marks", color="Subject", title="Subject-wise class average"), use_container_width=True)
with right:
    st.subheader("Pass vs Fail")
    result_counts = filtered["Result"].value_counts().rename_axis("Result").reset_index(name="Students")
    st.plotly_chart(px.pie(result_counts, names="Result", values="Students", hole=.4, title="Result distribution"), use_container_width=True)

st.subheader("Percentage Distribution")
st.plotly_chart(px.histogram(filtered, x="Percentage", nbins=20, title="How student percentages are distributed", labels={"Percentage":"Percentage (%)"}), use_container_width=True)

st.subheader("Top 10 Students")
top10 = filtered.sort_values("Percentage", ascending=False).head(10)
st.dataframe(top10[["Student_ID","Student_Name","Class","Total_Marks","Percentage","Result"]], use_container_width=True, hide_index=True)

st.subheader("Student Records")
st.dataframe(filtered, use_container_width=True, hide_index=True)
st.download_button("⬇️ Download filtered results (CSV)", filtered.to_csv(index=False).encode("utf-8"), "student_results_filtered.csv", "text/csv")

with st.expander("Project details for viva"):
    st.markdown("""
    **Aim:** To analyze student academic performance using Python, Pandas, Plotly and Streamlit.

    **Workflow:** CSV data ingestion → data validation and numeric conversion → filter by class/result → calculate totals and percentages → visualize subject averages and pass/fail distribution → export results.

    **Big Data concepts demonstrated:** dataset ingestion, data cleaning, aggregation, filtering, KPI summaries, visualization and data export.

    **Dataset note:** This project uses generated sample data (1,200 student records) for demonstration. It is a Big Data analytics prototype, not a distributed Hadoop/Spark cluster.
    """)
