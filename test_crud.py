from backend.crud import (
    call_add_new_book,
    call_add_new_borrower,
    add_new_loan,
    return_book,
    list_all_entries_from,
    list_all_loans,
)
from datetime import date

print("🔧 Running CRUD tests...")

# Test data
test_title = "Test Book"
test_author = "Test Author"
test_genre = "Test Genre"
test_language = "English"

test_fname = "Test"
test_lname = "User"
test_phone = "1234567890"
test_email = "test@example.com"

try:
    print("➕ Adding test book...")
    result = call_add_new_book(test_title, test_author, test_genre, test_language)
    print("✅ Book added:", result)

    print("➕ Adding test borrower...")
    result = call_add_new_borrower(test_fname, test_lname, test_phone, test_email)
    print("✅ Borrower added:", result)

    print("📚 Fetching books and borrowers...")
    books = list_all_entries_from('Book')
    loans_before = list_all_loans()
    last_book = books[-1]
    book_id = last_book.book_id

    from backend.crud import get_all_borrowers
    borrower_id = get_all_borrowers()[-1]["id"]

    print("📖 Lending the book...")
    loan_success, msg = add_new_loan(borrower_id, book_id, date.today())
    print("✅ Loan result:", msg)

    print("📥 Returning the book...")
    return_success, msg = return_book(book_id, date.today())
    print("✅ Return result:", msg)

    print("📋 All books:")
    for book in books:
        print(f"- {book.title}")

    print("📋 All loans:")
    loans_after = list_all_loans()
    for loan in loans_after:
        print(f"- {loan.title} borrowed by {loan.fname} {loan.lname}")

except Exception as e:
    print("❌ Error during test:", e)
