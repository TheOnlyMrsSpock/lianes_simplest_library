USE SimplestLib;

DELIMITER $$

CREATE PROCEDURE AddNewBook(
    IN p_title VARCHAR(255),
    IN p_author_name VARCHAR(100),
    IN p_genre_name VARCHAR(100),
    IN p_language VARCHAR(50)
)
BEGIN
    DECLARE v_author_id INT;
    DECLARE v_genre_id INT;

    -- Handle Author
    SELECT author_id INTO v_author_id FROM Author WHERE full_name = p_author_name;
    IF v_author_id IS NULL THEN
        INSERT INTO Author (full_name) VALUES (p_author_name);
        SET v_author_id = LAST_INSERT_ID();
    END IF;
    
    -- Handle Genre
    SELECT genre_id INTO v_genre_id FROM Genre WHERE name = p_genre_name;
    IF v_genre_id IS NULL THEN
        INSERT INTO Genre (name) VALUES (p_genre_name);
        SET v_genre_id = LAST_INSERT_ID();
    END IF;

    -- Insert Book
    INSERT INTO Book (title, author_id, genre_id, language) 
    VALUES (p_title, v_author_id, v_genre_id, p_language);

END $$


CREATE PROCEDURE AddNewBorrower(
    IN p_fname VARCHAR(100),
    IN p_lname VARCHAR(100),
    IN p_phone_number VARCHAR(20),
    IN p_email_address VARCHAR(255)
)
BEGIN
    -- Insert Borrower
    INSERT INTO Borrower (fname, lname, phone_number, email_address)
    VALUES (p_fname, p_lname, p_phone_number, p_email_address);
END $$


CREATE PROCEDURE AddNewLoan(
    IN p_borrower_id INT,
    IN p_book_id INT,
    IN p_date_of_borrowing DATE
)
BEGIN
    DECLARE v_book_on_loan INT;

    -- Check if the book is already on loan
    SELECT COUNT(*) INTO v_book_on_loan
    FROM Loan
    WHERE book_id = p_book_id AND return_date IS NULL;
    
    IF v_book_on_loan > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Book is currently on loan and cannot be borrowed.';
    ELSE
        -- Create Loan if the book is available
        INSERT INTO Loan (borrower_id, book_id, date_of_borrowing, due_date, return_date)
        VALUES (p_borrower_id, p_book_id, p_date_of_borrowing, DATE_ADD(p_date_of_borrowing, INTERVAL 14 DAY), NULL);
    END IF;

END $$


CREATE PROCEDURE ReturnBook(
    IN p_loan_id INT,
    IN p_return_date DATE
)
BEGIN
    -- Update the return date for the specified book in the loan
    UPDATE Loan
    SET return_date = p_return_date
    WHERE loan_id = p_loan_id AND return_date IS NULL;
END $$

CREATE PROCEDURE UpdateBook(
    IN p_book_id INT,
    IN p_title VARCHAR(255),
    IN p_language VARCHAR(50),
    IN p_author_name VARCHAR(100),
    IN p_genre_name VARCHAR(100)
)
BEGIN
    DECLARE v_author_id INT;
    DECLARE v_genre_id INT;

    -- Ensure author exists
    SELECT author_id INTO v_author_id
    FROM Author
    WHERE full_name = p_author_name;

    IF v_author_id IS NULL THEN
        INSERT INTO Author(full_name) VALUES (p_author_name);
        SELECT LAST_INSERT_ID() INTO v_author_id;
    END IF;

    -- Ensure genre exists
    SELECT genre_id INTO v_genre_id
    FROM Genre
    WHERE name = p_genre_name;

    IF v_genre_id IS NULL THEN
        INSERT INTO Genre(name) VALUES (p_genre_name);
        SELECT LAST_INSERT_ID() INTO v_genre_id;
    END IF;

    -- Update the book
    UPDATE Book
    SET title = p_title,
        language = p_language,
        author_id = v_author_id,
        genre_id = v_genre_id
    WHERE book_id = p_book_id;
END$$

CREATE PROCEDURE UpdateBorrower(
    IN p_borrower_id INT,
    IN p_fname VARCHAR(100),
    IN p_lname VARCHAR(100),
    IN p_phone_number VARCHAR(20),
    IN p_email_address VARCHAR(255)
)
BEGIN
    UPDATE Borrower
    SET fname = p_fname,
        lname = p_lname,
        phone_number = p_phone_number,
        email_address = p_email_address
    WHERE borrower_id = p_borrower_id;
END$$

DELIMITER ;
