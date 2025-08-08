import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

# === 1. Load Data ===
@st.cache_data
def load_data():
    df = pd.read_excel("data/book_data.xlsx", sheet_name="book tracker")
    df = df.rename(columns=lambda x: x.strip().lower())
    df["date finished reading"] = pd.to_datetime(df["date finished reading"], errors="coerce")
    df["pages"] = pd.to_numeric(df["pages"], errors="coerce")
    return df

df = load_data()

# === 2. Sidebar: Add Book (Prototype only, not persistent) ===
st.sidebar.header("Add New Book")
with st.sidebar.form("add_book_form"):
    title = st.text_input("Book Title")
    author = st.text_input("Author")
    pages = st.number_input("Number of Pages", min_value=1)
    start = st.date_input("Start Date")
    finish = st.date_input("Finish Date")
    submitted = st.form_submit_button("Submit")
    if submitted:
        st.warning("This prototype doesn't save to file yet.")

# === 3. Main App ===
st.title("📚 BookTracker Dashboard")
st.metric("Books Read", df["date finished reading"].notna().sum())
st.metric("Total Pages Read", int(df["pages"].sum()))

# === 4. Charts ===
st.subheader("Books Read Per Year")
if "date finished reading" in df:
    df["year"] = df["date finished reading"].dt.year
    count_by_year = df[df["date finished reading"].notna()]
    chart_data = count_by_year.groupby("year").size().reset_index(name="books_read")
    fig = px.bar(chart_data, x="year", y="books_read", title="Books Read Per Year")
    st.plotly_chart(fig)

st.subheader("Pages Read Per Week")
if "date finished reading" in df:
    df["week"] = df["date finished reading"].dt.isocalendar().week
    df["year"] = df["date finished reading"].dt.year
    pages_week = df.groupby(["year", "week"])['pages'].sum().reset_index()
    week_chart = alt.Chart(pages_week).mark_line().encode(
        x="week:O",
        y="pages:Q",
        color="year:N"
    ).properties(title="Pages Read Per Week")
    st.altair_chart(week_chart, use_container_width=True)
