import sqlite3
import pandas as pd
import streamlit as st


# Database Connection
def get_connection():
    conn = sqlite3.connect("library.db")
    return conn


# Create Table
conn = get_connection()
cursor = conn.cursor()
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        status TEXT NOT NULL
    )
"""
)
conn.commit()
conn.close()

# Website Title
st.title("📚 Library Management System")

# Sidebar - Operations
st.sidebar.header("Menu")
option = st.sidebar.selectbox(
    "Choose Action",
    [
        "View All Books",
        "Add Book",
        "Issue Book",
        "Return Book",
        "Delete Book",
    ],
)

# 1. View All Books
if option == "View All Books":
    st.subheader("Book Inventory")
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM books", conn)
    conn.close()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No books available in the library.")

# 2. Add Book
elif option == "Add Book":
    st.subheader("Add a New Book")
    title = st.text_input("Book Title")
    author = st.text_input("Author Name")
    if st.button("Add Book"):
        if title and author:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO books (title, author, status) VALUES (?, ?, ?)",
                (title, author, "Available"),
            )
            conn.commit()
            conn.close()
            st.success(f"'{title}' added successfully!")
        else:
            st.warning("Please fill in both fields.")

# 3. Issue Book
elif option == "Issue Book":
    st.subheader("Issue a Book")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM books WHERE status = 'Available'")
    available_books = cursor.fetchall()
    conn.close()

    if available_books:
        book_dict = {f"{b[1]} (ID: {b[0]})": b[0] for b in available_books}
        selected_book = st.selectbox(
            "Select Book to Issue", list(book_dict.keys())
        )
        if st.button("Issue"):
            book_id = book_dict[selected_book]
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE books SET status = 'Issued' WHERE id = ?", (book_id,)
            )
            conn.commit()
            conn.close()
            st.success("Book issued successfully!")
    else:
        st.info("No available books to issue.")

# 4. Return Book
elif option == "Return Book":
    st.subheader("Return a Book")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM books WHERE status = 'Issued'")
    issued_books = cursor.fetchall()
    conn.close()

    if issued_books:
        book_dict = {f"{b[1]} (ID: {b[0]})": b[0] for b in issued_books}
        selected_book = st.selectbox(
            "Select Book to Return", list(book_dict.keys())
        )
        if st.button("Return"):
            book_id = book_dict[selected_book]
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE books SET status = 'Available' WHERE id = ?", (book_id,)
            )
            conn.commit()
            conn.close()
            st.success("Book returned successfully!")
    else:
        st.info("No issued books to return.")

# 5. Delete Book
elif option == "Delete Book":
    st.subheader("Delete a Book")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM books")
    all_books = cursor.fetchall()
    conn.close()

    if all_books:
        book_dict = {f"{b[1]} (ID: {b[0]})": b[0] for b in all_books}
        selected_book = st.selectbox(
            "Select Book to Delete", list(book_dict.keys())
        )
        if st.button("Delete"):
            book_id = book_dict[selected_book]
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
            conn.commit()
            conn.close()
            st.success("Book deleted successfully!")
    else:
        st.info("No books to delete.")