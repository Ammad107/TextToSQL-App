import streamlit as st
import pandas as pd
import sqlite3
from langchain_community.utilities import SQLDatabase
from langchain_groq import ChatGroq  # Changed from Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Page Setup
st.set_page_config(page_title="AI Data Pro", layout="wide")
st.title("🚀 Cloud-Powered Text-to-SQL")

# Database Connection
db_path = "student_grades.db"
db = SQLDatabase.from_uri(f"sqlite:///{db_path}")

# Initialize Groq (The Cloud Brain)
# Replace 'YOUR_GROQ_API_KEY' with the key you just got
llm = ChatGroq(
    api_key="YOUR_GROQ_API_KEY", 
    model_name="llama-3.1-8b-instant",
    temperature=0
)

# Advanced Prompt
prompt = ChatPromptTemplate.from_template("""
You are a SQL expert. Write a SQL query for the following:
Schema: {schema}
Question: {question}
Return ONLY the SQL query.
""")

sql_chain = (prompt | llm | StrOutputParser())
schema = db.get_table_info()

# UI Logic
question = st.text_input("Ask your database a question:")

if question:
    try:
        sql_query = sql_chain.invoke({"schema": schema, "question": question}).strip()
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(sql_query, conn)
        conn.close()

        st.subheader("📊 Visualization")
        st.bar_chart(data=df, x=df.columns[0], y=df.columns[-1])
        st.dataframe(df)
    except Exception as e:
        st.error(f"Error: {e}")