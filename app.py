import streamlit as st
import os
import sqlite3
import time
from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, GoogleAPIError

load_dotenv()
api_key = os.getenv("AIzaSyB9jTTHDGERtx2ZnOygvianlZ5UcLzNm_M")
demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"

if not api_key and not demo_mode:
    st.error("API key not found. Please set GOOGLE_API_KEY in your .env file.")
    st.stop()

if not demo_mode:
    genai.configure(api_key=api_key)

# Model setup
available_models = ["gemini-2.0-flash", "gemini-1.5-flash"] # Preferred models for reliability
model_to_use = available_models[0]

# Mock demo data for testing without API quota
mock_queries = {
    "all students": "SELECT * FROM STUDENT;",
    "count": "SELECT COUNT(*) FROM STUDENT;",
    "data science": "SELECT * FROM STUDENT WHERE CLASS='Data Science';",
    "infosys": "SELECT * FROM STUDENT WHERE COMPANY='Infosys';",
    "tcs": "SELECT * FROM STUDENT WHERE COMPANY='TCS';",
    "highest marks": "SELECT * FROM STUDENT ORDER BY MARKS DESC LIMIT 1;",
    "web development": "SELECT * FROM STUDENT WHERE CLASS='Web Development';",
    "google": "SELECT * FROM STUDENT WHERE COMPANY='Google';",
    "amazon": "SELECT * FROM STUDENT WHERE COMPANY='Amazon';",
}

# Prompt engineering as per document logic
prompt = [
    """
    You are an expert in converting English questions to SQL queries!
    The SQL database is named STUDENT and has columns: NAME, CLASS, SECTION, MARKS, and COMPANY.
    Example 1: "How many entries of records are present?" -> SELECT COUNT(*) FROM STUDENT;
    Example 2: "Tell me all students in Data Science?" -> SELECT * FROM STUDENT WHERE CLASS="Data Science";
    
    IMPORTANT: Return ONLY the SQL query. No backticks, no 'sql' word, just the code.
    """
]

def get_gemini_response(question, prompt, max_retries=3):
    # Demo mode: return mock SQL without calling API
    if demo_mode:
        question_lower = question.lower()
        for keyword, sql in mock_queries.items():
            if keyword in question_lower:
                return sql
        # Fallback for unrecognized queries in demo mode
        return "SELECT * FROM STUDENT LIMIT 5;"
    
    model = genai.GenerativeModel(model_to_use)
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content([prompt[0], question])
            return response.text.strip().replace("```sql", "").replace("```", "").strip()
        except ResourceExhausted as e:
            # Quota exceeded - provide helpful error message
            if attempt == max_retries - 1:
                raise Exception(
                    "❌ **API Quota Exceeded**\n\n"
                    "You've hit the free tier limit for the Gemini API.\n\n"
                    "**Quick Fix:** Enable Demo Mode!\n"
                    "Set `DEMO_MODE=true` in your .env file to test without API calls.\n\n"
                    "**Permanent Options:**\n"
                    "1. **Wait**: Quotas reset daily at midnight UTC\n"
                    "2. **Upgrade**: Get a paid plan at https://ai.google.dev/pricing\n"
                    "3. **Monitor**: Check usage at https://ai.google.dev/rate-limits"
                )
            wait_time = min(2 ** attempt, 10)  # Exponential backoff, max 10 seconds
            time.sleep(wait_time)
        except GoogleAPIError as e:
            raise Exception(f"API Error: {str(e)}")
    
    return None

def read_sql_query(sql, db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    conn.close()
    return rows

# --- PAGE FUNCTIONS ---

def page_home():
    st.markdown("<h1 style='text-align: center;'>Welcome to <span style='color: #00D1FF;'>IntelliSQL</span>!</h1>", unsafe_allow_html=True)
    st.markdown("### Revolutionizing Database Querying with Advanced LLM Capabilities")
    
    st.write("""
    IntelliSQL is a powerful tool designed to bridge the gap between natural language and complex SQL databases. 
    By leveraging Gemini Pro, we allow users to talk to their data directly.
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("#### 🚀 Intelligent Assistance\nNovice or expert, craft queries with ease.")
    with col2:
        st.success("#### 📊 Data Insights\nUncover patterns and trends instantly.")

def page_about():
    st.title("About IntelliSQL")
    st.write("""
    **IntelliSQL** serves as a bridge for data analysts and researchers. 
    It simplifies the exploration process by translating human language into executable SQL commands.
    
    **Key Technologies:**
    - **Streamlit:** For the interactive UI.
    - **Gemini Pro:** The LLM engine for Natural Language Processing.
    - **SQLite:** The underlying database engine.
    """)

def page_intelligent_query_assistance():
    st.header("NLP to SQL Query Conversion")
    
    if demo_mode:
        st.info("🔧 **Demo Mode Active** - Using mock queries instead of API (no quota consumed)")
        st.caption("Example questions: 'Show all students', 'Count records', 'Data Science students', 'Infosys employees'")
    
    question = st.text_input("Enter your question in plain English:", placeholder="e.g., Show me all students working at Infosys")
    
    if st.button("Generate & Execute"):
        if question:
            with st.spinner('Generating SQL...'):
                try:
                    sql_query = get_gemini_response(question, prompt)
                    st.subheader("Generated SQL Query:")
                    st.code(sql_query, language='sql')
                    
                    try:
                        data = read_sql_query(sql_query, "data.db")
                        st.subheader("Query Results:")
                        if data:
                            st.table(data) # Using table for better visual alignment with the doc
                        else:
                            st.warning("No records found.")
                    except Exception as e:
                        st.error(f"Database Error: {e}")
                except Exception as e:
                    st.error(str(e))
        else:
            st.warning("Please enter a question first.")

# --- MAIN APP STRUCTURE ---

def main():
    st.set_page_config(page_title="IntelliSQL", page_icon="⭐", layout="wide")

    # Custom Sidebar Styling (Matching the dark #2E2E2E background in doc)
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {
                background-color: #2E2E2E;
                color: white;
            }
            [data-testid="stSidebar"] * {
                color: white !format;
            }
        </style>
    """, unsafe_allow_html=True)

    st.sidebar.title("Navigation")
    pages = {
        "Home": page_home,
        "About": page_about,
        "Intelligent Query Assistance": page_intelligent_query_assistance
    }
    
    selection = st.sidebar.radio("Select Page", list(pages.keys()))
    
    # Render the selected page
    pages[selection]()

if __name__ == "__main__":

    main()
