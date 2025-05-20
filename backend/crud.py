from sqlalchemy import create_engine, text
from backend.db_setup import engine
import pandas as pd

# ----------------------------
# Add a new book
# ----------------------------
def call_add_new_book(title, author, genre, language):
    try:
        query = text("CALL AddNewBook(:p_title, :p_author, :p_genre, :p_language)")
        params = {
                    "p_title": title,
                    "p_author": author,
                    "p_genre": genre,
                    "p_language": language
                }
        with engine.connect() as connection:
            with connection.begin():
                connection.execute(query, params)
        return True
    except Exception as e:
        return str(e)

# ----------------------------
# Add a new borrower
# ----------------------------
def call_add_new_borrower(fname, lname, phone, email):
    try:
        query = text("CALL AddNewBorrower(:p_fname, :p_lname, :p_phone_number, :p_email_address)")
        params = {
                    "p_fname": fname,
                    "p_lname": lname,
                    "p_phone_number": phone,
                    "p_email_address": email
                }
        with engine.connect() as connection:
            with connection.begin():
                connection.execute(query, params)
        return True
    except Exception as e:
        return str(e)

# ----------------------------
# Create a loan
# ----------------------------
def add_new_loan(borrower_id, book_id, date_of_borrowing):
    try:
        query = text("CALL AddNewLoan(:p_borrower_id, :p_book_id, :p_date_of_borrowing)")
        params = {
                    "p_borrower_id": borrower_id,
                    "p_book_id": book_id,
                    "p_date_of_borrowing": date_of_borrowing
                }
        with engine.connect() as connection:
            with connection.begin():
                connection.execute(query, params)
        return True, "Loan created successfully."
    except Exception as e:
        return False, str(e)

# ----------------------------
# Return a book
# ----------------------------
def return_book(book_id, return_date):
    try:
        query = text("CALL ReturnBook(:p_book_id, :p_return_date)")
        params = {
                    "p_book_id": book_id,
                    "p_return_date": return_date
                }
        with engine.connect() as connection:
            with connection.begin():
                connection.execute(query, params)
        return True, "Book returned successfully."
    except Exception as e:
        return False, str(e)

# ----------------------------
# Update a book
# ----------------------------
def update_book(book_id, title, language, author, genre):
    try:
        query = text("CALL UpdateBook(:p_book_id, :p_title, :p_language, :p_author, :p_genre)")
        params = {
                    "p_book_id": book_id,
                    "p_title": title,
                    "p_language": language,
                    "p_author": author,
                    "p_genre": genre
                }
        with engine.connect() as connection:
            with connection.begin():
                connection.execute(query, params)
        return True, "Book updated successfully."
    except Exception as e:
        return False, str(e)

# ----------------------------
# Update a borrower
# ----------------------------
def update_borrower(borrower_id, fname, lname, phone, email):
    try:
        query = text("CALL UpdateBorrower(:p_borrower_id, :p_fname, :p_lname, :p_phone_number, :p_email_address)")
        params = {
                    "p_borrower_id": borrower_id,
                    "p_fname": fname,
                    "p_lname": lname,
                    "p_phone_number": phone,
                    "p_email_address": email
                }
        with engine.connect() as connection:
            with connection.begin():
                connection.execute(query, params)
        return True, "Borrower updated successfully."
    except Exception as e:
        return False, str(e)

# ----------------------------
# List all entries from a table
# ----------------------------
def list_all_entries_from(table_name):
    query = text(f"SELECT * FROM {table_name}")
    with engine.connect() as connection:
        result = connection.execute(query)
        return result.fetchall()

# ----------------------------
# List all loans
# ----------------------------
def list_all_loans():
    query = text("""
        SELECT l.loan_id, b.title, br.fname, br.lname, 
               l.date_of_borrowing, l.due_date, l.return_date
        FROM Loan l
        JOIN Book b ON l.book_id = b.book_id
        JOIN Borrower br ON l.borrower_id = br.borrower_id
        ORDER BY l.loan_id DESC
    """)
    with engine.connect() as connection:
        result = connection.execute(query)
        return result.fetchall()

# ----------------------------
# List active loans only
# ----------------------------
def list_active_loans():
    query = text("""
        SELECT l.loan_id, b.title, br.fname, br.lname, 
               l.date_of_borrowing, l.due_date
        FROM Loan l
        JOIN Book b ON l.book_id = b.book_id
        JOIN Borrower br ON l.borrower_id = br.borrower_id
        WHERE l.return_date IS NULL
        ORDER BY l.due_date ASC
    """)
    with engine.connect() as connection:
        result = connection.execute(query)
        return result.fetchall()

# ----------------------------
# Get book details
# ----------------------------
def get_book_details(book_id):
    query = text("""
        SELECT b.title, a.full_name AS author, g.name AS genre, b.language
        FROM Book b
        JOIN Author a ON b.author_id = a.author_id
        JOIN Genre g ON b.genre_id = g.genre_id
        WHERE b.book_id = :book_id
    """)
    with engine.connect() as connection:
        result = connection.execute(query, {"book_id": book_id})
        return result.fetchone()

# ----------------------------
# Get borrower details      
# ----------------------------
def get_borrower_details(borrower_id):
    query = text("""
        SELECT fname, lname, phone_number, email_address
        FROM Borrower
        WHERE borrower_id = :borrower_id
    """)
    with engine.connect() as connection:
        result = connection.execute(query, {"borrower_id": borrower_id})
        return result.fetchone()
    
# ----------------------------
# Get library stats
# ----------------------------

def get_library_stats():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT
                (SELECT COUNT(*) FROM Borrower) AS total_borrowers,
                (SELECT COUNT(DISTINCT borrower_id) FROM Loan WHERE return_date IS NULL) AS active_borrowers,
                (SELECT COUNT(*) FROM Book) AS total_books,
                (SELECT COUNT(*) FROM Loan WHERE return_date IS NULL) AS borrowed_books
        """)).fetchone()
        
        return {
            "total_borrowers": result[0],
            "active_borrowers": result[1],
            "total_books": result[2],
            "borrowed_books": result[3],
        }

def get_book_loan_stats():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                SUM(CASE 
                    WHEN EXISTS (
                        SELECT 1 FROM Loan l WHERE l.book_id = b.book_id AND l.return_date IS NULL
                    ) THEN 1 ELSE 0 
                END) AS borrowed,
                SUM(CASE 
                    WHEN NOT EXISTS (
                        SELECT 1 FROM Loan l WHERE l.book_id = b.book_id AND l.return_date IS NULL
                    ) THEN 1 ELSE 0 
                END) AS available
            FROM Book b
        """)).fetchone()
    return {"Borrowed": result[0], "Available": result[1]}

def get_top_borrowers():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                CONCAT(b.fname, ' ', b.lname) AS borrower,
                COUNT(*) AS books_on_loan
            FROM Loan l
            JOIN Borrower b ON l.borrower_id = b.borrower_id
            WHERE l.return_date IS NULL
            GROUP BY b.borrower_id
            ORDER BY books_on_loan DESC
            LIMIT 10
        """))
        return pd.DataFrame(result.fetchall(), columns=result.keys())

# Helper functions for dropdowns and searches

def get_all_borrowers():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT borrower_id, fname, lname FROM Borrower"))
        return [{"id": row.borrower_id, "name": f"{row.fname} {row.lname}"} for row in result]

def get_all_books():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT book_id, title FROM Book"))
        return [{"id": row.book_id, "title": row.title} for row in result]

def get_all_books_status():
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT 
                b.book_id,
                b.title,
                a.full_name AS author,
                g.name AS genre,
                b.language,
                CASE 
                    WHEN EXISTS (
                        SELECT 1 FROM Loan l 
                        WHERE l.book_id = b.book_id AND l.return_date IS NULL
                    ) THEN 'Borrowed'
                    ELSE 'Available'
                END AS status
            FROM Book b
            LEFT JOIN Author a ON b.author_id = a.author_id
            LEFT JOIN Genre g ON b.genre_id = g.genre_id
        """))
        return pd.DataFrame(result.fetchall(), columns=result.keys())

def style_book_status(df):
    def highlight_status(status):
        if status == 'Available':
            return 'background-color: #d4edda; color: #155724;'  # green
        elif status == 'Borrowed':
            return 'background-color: #f8d7da; color: #721c24;'  # red
        return ''
    return df.style.applymap(highlight_status, subset=['status'])

def search_borrowers(term):
    return [b for b in get_all_borrowers() if term.lower() in b["name"].lower()]

def search_books(term):
    return [b for b in get_all_books() if term.lower() in b["title"].lower()]

def get_borrowed_books():
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT l.book_id, b.title, a.full_name AS author, br.fname, br.lname
            FROM Loan l
            JOIN Book b ON l.book_id = b.book_id
            JOIN Author a ON b.author_id = a.author_id
            JOIN Borrower br ON l.borrower_id = br.borrower_id
            WHERE l.return_date IS NULL
        """))
        return [
            {
                "id": row.book_id,
                "title": f"{row.title} by {row.author} (borrowed by {row.fname} {row.lname})"
            }
            for row in result
        ]

def search_borrowed_books(term):
    return [book for book in get_borrowed_books() if term.lower() in book["title"].lower()]
