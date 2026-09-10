import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Smart LMS - Enterprise Portal",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Professional Styling
st.markdown("""
<style>
    /* Global Styles */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Title Styling */
    .title-text {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 0px;
    }
    
    .sub-title {
        color: #4B5563;
        font-size: 16px;
        margin-bottom: 25px;
    }

    /* Metric Card Customization */
    [data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: bold;
        color: #1F2937;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0F172A;
        color: white;
    }
    
    [data-testid="stSidebar"] label {
        color: #E2E8F0 !important;
    }
    
    /* Buttons Styling */
    .stButton>button {
        background-color: #2563EB;
        color: white;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #1D4ED8;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Database Initialization
# ---------------------------------------------------------
def get_db_connection():
    conn = sqlite3.connect('library.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS books (
            book_id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            category TEXT NOT NULL,
            status TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS issue_records (
            record_id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            student_id TEXT NOT NULL,
            student_name TEXT NOT NULL,
            issue_date TEXT NOT NULL,
            return_date TEXT,
            fine_collected REAL DEFAULT 0,
            FOREIGN KEY (book_id) REFERENCES books (book_id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ---------------------------------------------------------
# Header & Navigation
# ---------------------------------------------------------
st.markdown("<h1 class='title-text'>📚 Smart Library Management System</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Next-Gen Digital Portal for College Libraries</p>", unsafe_allow_html=True)

# Sidebar Options
st.sidebar.image("https://img.icons8.com/isometric/100/book.png", width=70)
st.sidebar.title("Navigation Panel")
menu = ["📊 Executive Dashboard", "🔍 Catalog Search", "🔄 Book Operations (Issue/Return)", "➕ Admin Management"]
choice = st.sidebar.radio("Select Action", menu)

conn = get_db_connection()

# ---------------------------------------------------------
# 1. Executive Dashboard
# ---------------------------------------------------------
if choice == "📊 Executive Dashboard":
    st.subheader("📊 Real-time Library Overview")
    
    df_books = pd.read_sql_query("SELECT * FROM books", conn)
    df_records = pd.read_sql_query("SELECT * FROM issue_records", conn)
    
    total_books = len(df_books)
    available_books = len(df_books[df_books['status'] == 'Available']) if not df_books.empty else 0
    issued_books = len(df_books[df_books['status'] == 'Issued']) if not df_books.empty else 0
    total_fine = df_records['fine_collected'].sum() if not df_records.empty else 0.0

    # Metric Cards
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📖 Total Books", total_books)
    col2.metric("✅ Available", available_books)
    col3.metric("📤 Issued", issued_books)
    col4.metric("💰 Fine Collected", f"₹{total_fine:.2f}")

    st.markdown("---")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.write("### 📈 Availability Distribution")
        if not df_books.empty:
            status_counts = df_books['status'].value_counts()
            st.bar_chart(status_counts)
        else:
            st.info("No data available to display chart.")
            
    with col_chart2:
        st.write("### 🏷️ Category Breakdown")
        if not df_books.empty:
            cat_counts = df_books['category'].value_counts()
            st.pie_chart(cat_counts)
        else:
            st.info("No category data available.")

# ---------------------------------------------------------
# 2. Catalog Search
# ---------------------------------------------------------
elif choice == "🔍 Catalog Search":
    st.subheader("🔍 Search Library Repository")
    
    df_books = pd.read_sql_query("SELECT * FROM books", conn)
    
    col_search, col_filter = st.columns([3, 1])
    with col_search:
        search_query = st.text_input("Enter Title, Author, or Book ID:")
    with col_filter:
        status_filter = st.selectbox("Status Filter", ["All", "Available", "Issued"])

    filtered_df = df_books.copy()
    
    if search_query:
        filtered_df = filtered_df[
            filtered_df['title'].str.contains(search_query, case=False, na=False) |
            filtered_df['author'].str.contains(search_query, case=False, na=False) |
            filtered_df['book_id'].astype(str).str.contains(search_query, na=False)
        ]
        
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
        
    st.write(f"Showing **{len(filtered_df)}** result(s):")
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# 3. Book Operations (Issue / Return)
# ---------------------------------------------------------
elif choice == "🔄 Book Operations (Issue/Return)":
    st.subheader("🔄 Issue & Return Transaction Desk")
    
    tab1, tab2 = st.tabs(["📤 Issue Book", "📥 Return Book & Calculate Fine"])
    
    with tab1:
        st.write("#### Issue Book to Student")
        col_a, col_b = st.columns(2)
        with col_a:
            stu_id = st.text_input("Student Roll Number:", placeholder="e.g., 21CSE045")
            stu_name = st.text_input("Student Name:")
        with col_b:
            book_id_issue = st.number_input("Book ID to Issue:", min_value=1, step=1)
            issue_date = st.date_input("Issue Date", datetime.now())
            
        if st.button("Process Issue"):
            if stu_id and stu_name:
                c = conn.cursor()
                c.execute("SELECT status, title FROM books WHERE book_id=?", (book_id_issue,))
                res = c.fetchone()
                
                if res and res['status'] == 'Available':
                    c.execute("UPDATE books SET status='Issued' WHERE book_id=?", (book_id_issue,))
                    c.execute("""
                        INSERT INTO issue_records (book_id, student_id, student_name, issue_date)
                        VALUES (?, ?, ?, ?)
                    """, (book_id_issue, stu_id, stu_name, str(issue_date)))
                    conn.commit()
                    st.toast(f"Success! '{res['title']}' issued to {stu_name}.", icon="✅")
                    st.success(f"Book ID {book_id_issue} issued successfully!")
                else:
                    st.error("Error: Book is either already Issued or Book ID does not exist.")
            else:
                st.warning("Please enter complete student details.")

    with tab2:
        st.write("#### Return Book & Automatic Fine Calculator")
        col_c, col_d = st.columns(2)
        with col_c:
            book_id_return = st.number_input("Book ID to Return:", min_value=1, step=1)
            return_date = st.date_input("Return Date", datetime.now())
        with col_d:
            days_held = st.number_input("Total Days Book Kept:", min_value=1, value=14)
            
        if st.button("Process Return"):
            c = conn.cursor()
            c.execute("SELECT status, title FROM books WHERE book_id=?", (book_id_return,))
            res = c.fetchone()
            
            if res and res['status'] == 'Issued':
                # Fine Logic: > 14 days, charge Rs. 5/day
                fine = 0.0
                if days_held > 14:
                    fine = (days_held - 14) * 5.0
                    
                c.execute("UPDATE books SET status='Available' WHERE book_id=?", (book_id_return,))
                c.execute("""
                    UPDATE issue_records 
                    SET return_date=?, fine_collected=? 
                    WHERE book_id=? AND return_date IS NULL
                """, (str(return_date), fine, book_id_return))
                conn.commit()
                
                st.toast(f"Returned '{res['title']}' successfully!", icon="🎉")
                if fine > 0:
                    st.warning(f"⚠️ Late Return Penalty: ₹{fine:.2f} (Charge ₹5/day for {days_held - 14} extra days)")
                else:
                    st.success("Book returned on time. No fine applicable!")
            else:
                st.error("Error: This book is currently marked as Available or invalid ID.")

# ---------------------------------------------------------
# 4. Admin Management
# ---------------------------------------------------------
elif choice == "➕ Admin Management":
    st.subheader("🛠️ Librarian Admin Dashboard")
    
    with st.expander("➕ Add New Book Entry", expanded=True):
        with st.form("add_book_form", clear_on_submit=True):
            col_in1, col_in2 = st.columns(2)
            with col_in1:
                new_id = st.number_input("Unique Book ID:", min_value=101, step=1)
                new_title = st.text_input("Book Title:")
            with col_in2:
                new_author = st.text_input("Author Name:")
                new_category = st.selectbox("Category:", ["Computer Science", "Electrical", "Mechanical", "Civil", "Mathematics", "General Literature"])
                
            submit_btn = st.form_submit_button("Add Book to Database")
            
            if submit_btn:
                if new_title and new_author:
                    try:
                        c = conn.cursor()
                        c.execute("INSERT INTO books VALUES (?, ?, ?, ?, 'Available')", 
                                  (new_id, new_title, new_author, new_category))
                        conn.commit()
                        st.toast(f"Added '{new_title}' successfully!", icon="📚")
                        st.success(f"Book '{new_title}' (ID: {new_id}) saved to permanent database!")
                    except sqlite3.IntegrityError:
                        st.error("Error: Book ID already exists! Please use a unique ID.")
                else:
                    st.warning("Please fill out all mandatory fields.")

    st.markdown("---")
    st.write("### 📋 Current Active Database View")
    df_all = pd.read_sql_query("SELECT * FROM books", conn)
    st.dataframe(df_all, use_container_width=True)
    
