import streamlit as st
import pandas as pd
import psycopg2

# ---------------------- CONFIG ----------------------
DB_CONFIG = {
    'host': 'aws-0-eu-north-1.pooler.supabase.com',
    'dbname': 'postgres',
    'user': 'postgres.cgrpfqixtfxdcrvebeag',
    'password': 'YOUR_SUPABASE_PASSWORD',  # Replace with your actual password
    'port': '6543'
}

# ---------------------- DB Connection ----------------------
def get_connection():
    return psycopg2.connect(**DB_CONFIG)

# ---------------------- Streamlit App ----------------------
st.set_page_config(page_title="📊 Upload Nutrition Excel", layout="wide")
st.title("📂 Upload Nutrition Excel File")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])

if uploaded_file:
    if uploaded_file.name.endswith(".xls"):
        df = pd.read_excel(uploaded_file, engine='xlrd')
    else:
        df = pd.read_excel(uploaded_file)

    st.write("Preview of uploaded data:", df.head())

    if st.button("Store in SQL"):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            table_name = "uploaded_data"
            columns = df.columns.tolist()
            placeholders = ', '.join(['%s'] * len(columns))
            column_names = ', '.join(columns)

            # Auto-create table
            create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {table_name} (
    {', '.join([f'{col} TEXT' for col in columns])},
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
            cursor.execute(create_table_sql)

            # Insert data
            for _, row in df.iterrows():
                values = tuple(str(row[col]) for col in columns)
                insert_sql = f"""
INSERT INTO {table_name} ({column_names})
VALUES ({placeholders})
"""
                cursor.execute(insert_sql, values)

            conn.commit()
            cursor.close()
            conn.close()
            st.success("✅ Data stored in SQL!")
        except Exception as e:
            st.error(f"❌ Error: {e}")

if st.checkbox("📋 Show all stored data"):
    try:
        conn = get_connection()
        df_all = pd.read_sql_query("SELECT * FROM uploaded_data ORDER BY uploaded_at DESC", conn)
        conn.close()
        st.dataframe(df_all)
    except Exception as e:
        st.error(f"❌ Error fetching data: {e}")