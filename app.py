import streamlit as st
import pandas as pd
import sqlite3
from langchain_community.utilities import SQLDatabase
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. Page Setup
st.set_page_config(page_title="AI Data Pro", layout="wide")
st.title("🚀 Advanced Text-to-SQL Dashboard")

# 2. Database Connection
db_path = "student_grades.db"
db = SQLDatabase.from_uri(f"sqlite:///{db_path}")

# 3. Sidebar: Data Entry (Thing #1)
with st.sidebar:
    st.header("➕ Add New Student")
    with st.form("data_form"):
        new_name = st.text_input("Name")
        new_subject = st.selectbox("Subject", ["Math", "History", "Science"])
        new_score = st.number_input("Score", min_value=0, max_value=100)
        new_grade = st.selectbox("Grade", ["A", "B", "C", "D", "F"])
        submit = st.form_submit_button("Add to Database")
        
        if submit:
            conn = sqlite3.connect(db_path)
            curr = conn.cursor()
            curr.execute("INSERT INTO grades (name, subject, score, grade) VALUES (?, ?, ?, ?)", 
                         (new_name, new_subject, new_score, new_grade))
            conn.commit()
            conn.close()
            st.success(f"Added {new_name}!")

# 4. Advanced Prompt (Thing #2)
# Using a more detailed prompt helps the AI handle complex business logic
llm = ChatOllama(model="llama3.2:1b", temperature=0)
prompt = ChatPromptTemplate.from_template("""
You are a Senior Data Analyst. Given the database schema, write a SQL query.
Rules:
- Return ONLY the SQL code.
- If the user asks for 'best' or 'highest', sort by score DESC.
- If the user asks for 'average', use the AVG() function.
- Schema: {schema}
- Question: {question}
""")

sql_chain = (prompt | llm | StrOutputParser())
schema = db.get_table_info()

# 5. Main UI & Visualization (Thing #3)
question = st.text_input("Ask a question about your data:", placeholder="e.g., Show me a bar chart of scores by name")

if question:
    try:
        sql_query = sql_chain.invoke({"schema": schema, "question": question}).strip()
        
        # Run query and load into a Pandas DataFrame for visualization
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(sql_query, conn)
        conn.close()

        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Raw Data")
            st.dataframe(df)

        with col2:
            st.subheader("📊 Visualization")
            if not df.empty and len(df.columns) >= 2:
                # Automatically tries to plot the first two columns
                st.bar_chart(data=df, x=df.columns[0], y=df.columns[-1])
            else:
                st.info("Query a list (e.g., 'names and scores') to see a chart.")

    except Exception as e:
        st.error(f"Error: {e}")