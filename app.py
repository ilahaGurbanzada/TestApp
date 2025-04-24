import streamlit as st
import pandas as pd
import psycopg2
from psycopg2 import sql

# ---------------------- CONFIG ----------------------
DB_CONFIG = {
    'host': 'YOUR_HOST',
    'dbname': 'YOUR_DB_NAME',
    'user': 'YOUR_USERNAME',
    'password': 'YOUR_PASSWORD',
    'port': '5432'
}

# ---------------------- DB Connection ----------------------
def get_connection():
    return psycopg2.connect(**DB_CONFIG)

# ---------------------- Streamlit App ----------------------
st.set_page_config(page_title="📊 Upload Nutrition Excel", layout="wide")
st.title("📂 Upload Nutrition Excel File")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("Preview of uploaded data:", df.head())

    if st.button("Store in SQL"):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            for _, row in df.iterrows():
                cursor.execute(sql.SQL("""
                    INSERT INTO uploaded_data (col1, col2, col3)
                    VALUES (%s, %s, %s)
                """), (row["col1"], row["col2"], row["col3"]))

            conn.commit()
            cursor.close()
            conn.close()
            st.success("✅ Data stored in SQL!")
        except Exception as e:
            st.error(f"❌ Error: {e}")

if st.checkbox("📋 Show all stored data"):
    try:
        conn = get_connection()
        df_all = pd.read_sql_query("SELECT * FROM uploaded_data ORDER BY id DESC", conn)
        conn.close()
        st.dataframe(df_all)
    except Exception as e:
        st.error(f"❌ Error fetching data: {e}")