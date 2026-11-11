# Library Management System

A web application where a librarian can manage books and members, issue and return books, and have fines calculated automatically for late returns.

Built with **Python 3**, **Streamlit**, **SQLite (sqlite3)**, **datetime** and **pandas**.

## Features

- Add, delete and search books (by title or author)
- Register members as Student or Teacher
- Issue and return books
- Due date of 7 days from the issue date
- Fine of Rs. 10 for every late day, calculated automatically
- Borrow limit: Student 3 books, Teacher 5 books
- List of overdue books with the fine so far
- Dashboard with totals and a chart
- Librarian login
- All data saved in an SQLite database file (`library.db`)

## Project structure

| File | Job |
|---|---|
| `database.py` | Talks to the SQLite database: creates the tables, saves rows, reads rows |
| `logic.py` | The library rules: borrow limit, due date, fine, overdue list, login check |
| `app.py` | The Streamlit screens: login, sidebar menu and one page per feature |
| `sample_data.py` | Optional: adds 15 sample books to the database |
| `requirements.txt` | The outside libraries the app needs |

The database has three tables: `books`, `members` and `transactions`. A loan with an empty `return_date` is a book that is still out.

## How to run

1. Install the libraries:
   ```
   pip install -r requirements.txt
   ```
2. (Optional) Add 15 sample books:
   ```
   python sample_data.py
   ```
3. Start the app:
   ```
   streamlit run app.py
   ```
4. The browser opens at `http://localhost:8501`. Log in with:
   - Username: `admin`
   - Password: `admin123`

`library.db` is created automatically on the first run.

## Note on the code comments

Every line of code is tagged in its comment:

- `[CLASS nn]` marks a concept taught in that class notebook (for example `[CLASS 09]` for functions).
- `[NEW]` marks something not taught yet, added with the help of AI (sqlite3, SQL, datetime, Streamlit, pandas).

## Author

Akber Laasi
