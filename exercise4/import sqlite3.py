import sqlite3

# Create a new SQLite database and establish a connection
conn = sqlite3.connect('library.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Books (
        BookID INTEGER PRIMARY KEY,
        Title TEXT,
        Author TEXT,
        ISBN TEXT,
        Status TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        UserID INTEGER PRIMARY KEY,
        Name TEXT,
        Email TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Reservations (
        ReservationID INTEGER PRIMARY KEY,
        BookID INTEGER,
        UserID INTEGER,
        ReservationDate TEXT,
        FOREIGN KEY (BookID) REFERENCES Books(BookID),
        FOREIGN KEY (UserID) REFERENCES Users(UserID)
    )
''')
conn.commit()

# Function to add a new book to the Books table
def add_book(title, author, isbn, status):
    cursor.execute('''
        INSERT INTO Books (Title, Author, ISBN, Status)
        VALUES (?, ?, ?, ?)
    ''', (title, author, isbn, status))
    conn.commit()

# Function to find a book's details based on BookID
def find_book_by_id(book_id):
    cursor.execute('''
        SELECT Books.BookID, Title, Author, ISBN, Status, Users.Name, Users.Email
        FROM Books
        LEFT JOIN Reservations ON Books.BookID = Reservations.BookID
        LEFT JOIN Users ON Reservations.UserID = Users.UserID
        WHERE Books.BookID = ?
    ''', (book_id,))
    result = cursor.fetchone()
    return result

# Function to find a book's reservation status based on BookID, Title, UserID, and ReservationID
def find_reservation_status(text):
    if text.startswith('LB'):  # BookID
        cursor.execute('''
            SELECT BookID, Status
            FROM Books
            WHERE BookID = ?
        ''', (text,))
    elif text.startswith('LU'):  # UserID
        cursor.execute('''
            SELECT Books.BookID, Books.Status
            FROM Books
            INNER JOIN Reservations ON Books.BookID = Reservations.BookID
            WHERE Reservations.UserID = ?
        ''', (text,))
    elif text.startswith('LR'):  # ReservationID
        cursor.execute('''
            SELECT Books.BookID, Books.Status
            FROM Books
            INNER JOIN Reservations ON Books.BookID = Reservations.BookID
            WHERE Reservations.ReservationID = ?
        ''', (text,))
    else:  # Title
        cursor.execute('''
            SELECT Books.BookID, Title, Author, ISBN, Status, Users.Name, Users.Email
            FROM Books
            LEFT JOIN Reservations ON Books.BookID = Reservations.BookID
            LEFT JOIN Users ON Reservations.UserID = Users.UserID
            WHERE Books.Title = ?
        ''', (text,))
        
    result = cursor.fetchall()
    return result

# Function to find all books in the database
def find_all_books():
    cursor.execute('''
        SELECT Books.BookID, Title, Author, ISBN, Status, Users.Name, Users.Email
        FROM Books
        LEFT JOIN Reservations ON Books.BookID = Reservations.BookID
        LEFT JOIN Users ON Reservations.UserID = Users.UserID
    ''')
    result = cursor.fetchall()
    return result

# Function to modify/update book details based on BookID
def update_book_details(book_id, **kwargs):
    if 'status' in kwargs:
        cursor.execute('''
            UPDATE Books 
            SET Status = ?
            WHERE BookID = ?
        ''', (kwargs['status'], book_id))
        cursor.execute('''
            UPDATE Reservations 
            SET BookID = ?, ReservationDate = ?
            WHERE BookID = ?
        ''', (book_id, kwargs['reservation_date'], book_id))

        conn.commit()
        return "Book details and reservation status updated successfully."

    elif 'title' in kwargs:
        cursor.execute('''
            UPDATE Books 
            SET Title = ?
            WHERE BookID = ?
        ''', (kwargs['title'], book_id))
        conn.commit()
        return "Book title updated successfully."

    elif 'author' in kwargs:
        cursor.execute('''
            UPDATE Books 
            SET Author = ?
            WHERE BookID = ?
        ''', (kwargs['author'], book_id))
        conn.commit()
        return "Book author updated successfully."

    elif 'isbn' in kwargs:
        cursor.execute('''
            UPDATE Books 
            SET ISBN = ?
            WHERE BookID = ?
        ''', (kwargs['isbn'], book_id))
        conn.commit()
        return "Book ISBN updated successfully."

    else:
        return "No valid update options provided."

# Function to delete a book based on its BookID
def delete_book(book_id):
    cursor.execute('''
        DELETE FROM Reservations WHERE BookID = ?
    ''', (book_id,))
    cursor.execute('''
        DELETE FROM Books WHERE BookID = ?
    ''', (book_id,))
    conn.commit()
    return "Book deleted successfully."

# Function to close the database connection
def close_connection():
    cursor.close()
    conn.close()

# Main program loop
while True:
    print("\nLIBRARY MANAGEMENT SYSTEM")
    print("1. Add a new book to the database")
    print("2. Find a book's details based on BookID")
    print("3. Find a book's reservation status based on BookID, Title, UserID, or ReservationID")
    print("4. Find all the books in the database")
    print("5. Modify/update book details based on its BookID")
    print("6. Delete a book based on its BookID")
    print("7. Exit")

    choice = input("\nEnter your choice: ")

    if choice == '1':
        title = input("Enter the book title: ")
        author = input("Enter the book author: ")
        isbn = input("Enter the book ISBN: ")
        status = input("Enter the book status: ")
        add_book(title, author, isbn, status)
        print("Book added successfully.")

    elif choice == '2':
        book_id = input("Enter the BookID: ")
        result = find_book_by_id(book_id)
        if result is None:
            print("Book not found.")
        else:
            print("BookID:", result[0])
            print("Title:", result[1])
            print("Author:", result[2])
            print("ISBN:", result[3])
            print("Status:", result[4])
            if result[5] is None:
                print("Book not reserved.")
            else:
                print("Reserved by:", result[5])
                print("Reserved by Email:", result[6])

    elif choice == '3':
        text = input("Enter the BookID, Title, UserID, or ReservationID: ")
        result = find_reservation_status(text)
        if len(result) == 0:
            print("No matching book or reservation found.")
        else:
            for row in result:
                print("BookID:", row[0])
                print("Status:", row[1])

    elif choice == '4':
        result = find_all_books()
        if len(result) == 0:
            print("No books found in the database.")
        else:
            for row in result:
                print("BookID:", row[0])
                print("Title:", row[1])
                print("Author:", row[2])
                print("ISBN:", row[3])
                print("Status:", row[4])
                if row[5] is None:
                    print("Book not reserved.")
                else:
                    print("Reserved by:", row[5])
                    print("Reserved by Email:", row[6])

    elif choice == '5':
        book_id = input("Enter the BookID: ")
        update_option = input("Enter the update option (status, title, author, isbn): ")
        if update_option == 'status':
            status = input("Enter the new status: ")
            reservation_date = input("Enter the reservation date: ")
            result = update_book_details(book_id, status=status, reservation_date=reservation_date)
            print(result)
        elif update_option in ('title', 'author', 'isbn'):
            new_value = input(f"Enter the new {update_option}: ")
            result = update_book_details(book_id, **{update_option: new_value})
            print(result)
        else:
            print("Invalid update option.")

    elif choice == '6':
        book_id = input("Enter the BookID: ")
        result = delete_book(book_id)
        print(result)

    elif choice == '7':
        close_connection()
        break

    else:
        print("Invalid choice. Please try again.")