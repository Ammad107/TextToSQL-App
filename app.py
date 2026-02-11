import streamlit as st
import pandas as pd
import sqlite3
from langchain_community.utilities import SQLDatabase
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. Page Setup
st.set_page_config(page_title="AI Data Pro", layout="wide")
st.title("🚀 Professional AI Data Analyst")

# 2. Database Connection
db_path = "student_grades.db"
db = SQLDatabase.from_uri(f"sqlite:///{db_path}")

# 3. Sidebar: Manual Entry & Bulk Upload
with st.sidebar:
    st.header("📂 Data Management")
    
    # --- Bulk Upload Section ---
    st.subheader("Bulk Upload (CSV)")
    uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
    
    if uploaded_file is not None:
        try:
            # Read the uploaded CSV
            df_upload = pd.read_csv(uploaded_file)
            st.write("Preview:", df_upload.head(3))
            
            if st.button("Confirm Bulk Upload"):
                conn = sqlite3.connect(db_path)
                # This 'appends' the CSV data to your existing 'grades' table
                df_upload.to_sql("grades", conn, if_exists="append", index=False)
                conn.close()
                st.success("All data imported successfully!")
        except Exception as e:
            st.error(f"Upload error: {e}")
            
    st.markdown("---")
    
    # --- Manual Entry Section ---
    st.subheader("Add Single Entry")
    with st.form("manual_form"):
        new_name = st.text_input("Name")
        new_subject = st.selectbox("Subject", ["Math", "History", "Science", "English"])
        new_score = st.number_input("Score", 0, 100)
        new_grade = st.selectbox("Grade", ["A", "B", "C", "D", "F"])
        if st.form_submit_button("Add Student"):
            conn = sqlite3.connect(db_path)
            curr = conn.cursor()
            curr.execute("INSERT INTO grades (name, subject, score, grade) VALUES (?, ?, ?, ?)", 
                         (new_name, new_subject, new_score, new_grade))
            conn.commit()
            conn.close()
            st.success("Student added!")

# 4. AI Setup (Groq)
llm = ChatGroq(
    api_key=st.secrets["GROQ_API_KEY"], 
    model_name="llama-3.1-8b-instant",
    temperature=0
)

# Replace lines 65 through 69 with this:
prompt = ChatPromptTemplate.from_template("""
You are a SQL expert. Based on the schema, write a SQL query.
Return ONLY the SQL.
Schema: {schema}
Question: {question}
""")