import sys
import os

# Add the parent directory (project root) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import plotly.express as px
import streamlit as st
from streamlit_searchbox import st_searchbox
from backend.crud import *
from datetime import date

st.set_page_config(page_title="Liana's Literary Lounge", layout="centered")
st.title("📚 Liana's Literary Lounge")

# Sidebar navigation
menu = st.sidebar.selectbox("Navigate", [
    "Show Books", "Add New Book", "Add New Borrower", "Lend Book", "Return Book", "Update Entries", "STATS"
])

# Show books
if menu == "Show Books":
    st.header("📚 Overview of All Books in the Library")

    books_df = get_all_books_status()

    if books_df.empty:
        st.info("No books in the library yet.")
    else:
        books_df.reset_index(drop=True, inplace=True)

        def color_title_by_status(row):
            if row["status"] == "Available":
                return f'<span style="color:darkgreen;"><b>{row["title"]}</b></span>'
            elif row["status"] == "Borrowed":
                return f'<span style="color:darkred;"><b>{row["title"]}</b></span>'
            return row["title"]

        books_df["title"] = books_df.apply(color_title_by_status, axis=1)
        books_df.drop(columns=["status"], inplace=True)

        # index=False takes away column of index
        st.write(books_df.to_html(index=False, escape=False), unsafe_allow_html=True)

# Add new book
if menu == "Add New Book":
    st.header("📘 Add a New Book to the Library")

    # Initialisiere Reset-Flag beim ersten Start
    if "reset_book_form" not in st.session_state:
        st.session_state["reset_book_form"] = False

    # Initialisiere alle Eingabefelder bei erstem Lauf
    for key in ["book_title", "language", "author_name", "genre_name"]:
        if key not in st.session_state:
            st.session_state[key] = ""

    # Felder leeren, wenn Reset durch vorheriges Hinzufügen ausgelöst wurde
    if st.session_state["reset_book_form"]:
        for key in ["book_title", "language", "author_name", "genre_name"]:
            st.session_state[key] = ""
        st.session_state["reset_book_form"] = False

    # Eingabefelder mit Key-Bindung
    title = st.text_input("Book Title", key="book_title")
    language = st.text_input("Language", key="language")
    author_name = st.text_input("Author Full Name", key="author_name")
    genre_name = st.text_input("Genre Name", key="genre_name")

    # Button zum Hinzufügen
    if st.button("Add Book"):
        result = call_add_new_book(title, author_name, genre_name, language)
        if result is True:
            st.success("Book added successfully!")
            st.session_state["reset_book_form"] = True
            st.rerun()  # Neustart der App nach Reset
        else:
            st.error(result)


# Add new borrower
if menu == "Add New Borrower":
    st.header("👤 Add New Borrower to Liana’s Library")

    fname = st.text_input("First Name")
    lname = st.text_input("Last Name")
    phone = st.text_input("Phone Number")
    email = st.text_input("Email Address")

    if st.button("Add Borrower"):
        result = call_add_new_borrower(fname, lname, phone, email)
        if result is True:
            st.success("Borrower added successfully!")
        else:
            st.error(result)

# Lend a book
if menu == "Lend Book":
    st.header("📕 Lend a Book")

    borrower = st_searchbox(search_borrowers, key="search_borrower", placeholder="Search borrower by name")
    book = st_searchbox(search_books, key="search_book", placeholder="Search book by title")
    date_borrowed = st.date_input("Date of Borrowing", date.today())

    if st.button("Confirm Loan"):
        if not borrower or not book:
            st.warning("Please select both a borrower and a book.")
        else:
            success, message = add_new_loan(borrower_id=borrower["id"], book_id=book["id"], date_of_borrowing=date_borrowed)
            if success:
                st.success(message)
            else:
                st.error(f"Loan failed: {message}")

# Return a book
if menu == "Return Book":
    st.header("📥 Return a Book")

    selected_book = st_searchbox(search_borrowed_books, key="return_book", placeholder="Search borrowed book")
    return_date = st.date_input("Return Date", date.today())

    if st.button("Confirm Return"):
        if not selected_book:
            st.warning("Please select a borrowed book to return.")
        else:
            success, msg = return_book(selected_book["id"], return_date)
            if success:
                st.success(msg)
            else:
                st.error(f"Return failed: {msg}")

# Update entries in the database
if menu == "Update Entries":
    st.title("📘 Update Entries")

    tab1, tab2 = st.tabs(["📘 Update Book", "🧑‍💼 Update Borrower"])

    with tab1:
        st.header("📘 Update Book")

        # Fetch books
        books = list_all_entries_from('Book')
        book_dict = {f"{book[1]} (ID {book[0]})": book[0] for book in books}

        selected_book = st.selectbox("Select a book to update", list(book_dict.keys()))
        selected_book_id = book_dict[selected_book]

        book_data = get_book_details(selected_book_id)

        if selected_book:
            book_id = selected_book_id
            new_title = st.text_input("Title", value=book_data.title)
            new_language = st.text_input("Language", value=book_data.language)
            new_author = st.text_input("Author", value=book_data.author)
            new_genre = st.text_input("Genre", value=book_data.genre)

            if st.button("✅ Update Book"):

                success, msg = update_book(book_id, new_title, new_language, new_author, new_genre)
                if success:
                    st.success(msg)
                else:
                    st.error(f"Failed to update book: {msg}")

    with tab2:
        st.header("🧑‍💼 Update Borrower")

        # Fetch borrowers
        borrowers = list_all_entries_from('Borrower')
        borrower_dict = {f"{borrower[1]} {borrower[2]} (ID {borrower[0]})": borrower[0] for borrower in borrowers}

        selected_borrower = st.selectbox("Select a borrower to update", list(borrower_dict.keys()))
        selected_borrower_id = borrower_dict[selected_borrower]

        borrower_data = get_borrower_details(selected_borrower_id)

        if selected_borrower:
            borrower_id = borrower_dict[selected_borrower]
            new_fname = st.text_input("First Name", value=borrower_data.fname)
            new_lname = st.text_input("Last Name",value=borrower_data.lname)
            new_phone = st.text_input("Phone Number", value=borrower_data.phone_number)
            new_email = st.text_input("Email Address",value=borrower_data.email_address)

            if st.button("✅ Update Borrower"):

                success, msg = update_borrower(borrower_id, new_fname, new_lname, new_phone, new_email)
                if success:
                    st.success(msg)
                else:
                    st.error(f"Failed to update borrower: {msg}")

# Stats
if menu == "STATS":
    st.header("📊 Library Statistics")

    # Display general statistics
    stats = get_library_stats()

    col1, col2 = st.columns(2)

    with col1:
        st.metric(label="👥 Total Borrowers", value=stats["total_borrowers"])
        st.metric(label="📚 Total Books", value=stats["total_books"])

    with col2:
        st.metric(label="🟢 Active Borrowers", value=stats["active_borrowers"])
        st.metric(label="📕 Books on Loan", value=stats["borrowed_books"])

    # Display pie chart for book status
    stats = get_book_loan_stats()
    fig = px.pie(
        names=list(stats.keys()),
        values=list(stats.values()),
        title="Library Book Status",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig, use_container_width=True)

    # Display top borrowers
    top_borrowers_df = get_top_borrowers()

    st.subheader("🏆 Top 10 Borrowers by Number of Borrowed Books")
    if top_borrowers_df.empty:
        st.info("No active loans found.")
    else:
        fig1 = px.bar(top_borrowers_df, x="borrower", y="books_on_loan", color="books_on_loan",
                    labels={"books_on_loan": "Books on Loan"}, title="Top Borrowers",
                    color_continuous_scale='Blues')
        
    st.plotly_chart(fig1)