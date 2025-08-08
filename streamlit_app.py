import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import os

DATA_FILE = "data/book_data.csv"
# === 1. Load Data ===
@st.cache_data
def load_data():
    df = pd.read_excel("data/book_data.xlsx", sheet_name="book tracker")
    df = df.rename(columns=lambda x: x.strip().lower())
    df["date finished reading"] = pd.to_datetime(df["date finished reading"], errors="coerce")
    try:
       df["# of pages"] = pd.to_numeric(df["pages"], errors="coerce")
    except FileNotFoundError:
        st.error(f"The file {DATA_FILE} was not found.")
        st.stop()
    except pd.errors.EmptyDataError:
        return pd.DataFrame() # Return an empty DataFrame if the file is empty
    except pd.errors.ParserError:
        st.error(f"Error parsing the CSV file. Please check the file format.")
    except KeyError:
        st.error("The '# of pages' column was not found in the excel sheet.")
        st.stop()
    return df

df = load_data()

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# === 2. Sidebar: Add Book (Prototype only, not persistent) ===
st.sidebar.header("Add New Book")
with st.sidebar.form("add_book_form"):
    title = st.text_input("Book Title")
    author = st.text_input("Author")
    pages = st.number_input("Number of Pages", min_value=1)
    start_date = st.date_input("Start Date")
    finish_date = st.date_input("Finish Date")

    # Input Validation
    if start_date > finish_date:
        st.error("Error: Start date must be before finish date.")
        can_submit = False
    else:
        can_submit = True

    submitted = st.form_submit_button("Submit")
    if submitted and can_submit:
        new_book = pd.DataFrame([{
            "title": title,
            "author": author,
            "pages": pages,
            "date started reading": start_date,
            "date finished reading": finish_date
        }])

        #Handle empty dataframe
        if df is None or len(df) == 0:
            df = pd.concat([df, new_book], ignore_index=True)
        else:
            df = new_book

        save_data(df)
        st.success(f"Added book: {title} by {author} to {DATA_FILE}")

# Reload data to reflect changes
df = load_data()
data = df

# === 3. Main App ===
if 'pages' in df:
    st.title("📚 BookTracker Dashboard")

    #Check to ensure dates are valid
    df = df[df['date finished reading'].notna()]

    st.metric("Books Read", df["date finished reading"].notna().sum())
    st.metric("Total Pages Read", int(df["pages"].sum()))

# === 4. Charts ===
def create_books_per_year_chart(data):
   st.subheader("Books Read Per Year")
   if "date finished reading" in data:
       df["year"] = data["date finished reading"].dt.year
       count_by_year = data[data["date finished reading"].notna()]
       chart_data = count_by_year.groupby("year").size().reset_index(name="books_read")
       fig = px.bar(chart_data, x="year", y="books_read", title="Books Read Per Year")
       st.plotly_chart(fig)

def create_pages_per_week_chart(data):
   st.subheader("Pages Read Per Week")
   if "date finished reading" in data:
       df["week"] = data["date finished reading"].dt.isocalendar().week
       df["year"] = data["date finished reading"].dt.year
       pages_week = df.groupby(["year", "week"])['pages'].sum().reset_index()

       # Handle the case where week is a float
       pages_week['week'] = pages_week['week'].astype(int).astype(str)

       week_chart = alt.Chart(pages_week).mark_line().encode(

        x="week:O",
        y="pages:Q",
        color="year:N"

     ).properties(title="Pages Read Per Week")
   st.altair_chart(week_chart, use_container_width=True)

create_books_per_year_chart(data)
create_pages_per_week_chart(data)
