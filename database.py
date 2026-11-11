# =====================================================================
#  database.py  --->  FILE 1 of 3 : THE DATABASE LAYER
# ---------------------------------------------------------------------
#  Job of this file: talk to the SQLite database. Nothing else.
#  It does not know any library rules and it does not draw any screen.
#
#  How to read the tags in the comments:
#     [CLASS 09]  ---> taught in that class notebook
#     [NEW]       ---> not taught yet, added with the help of AI
# =====================================================================

# [NEW] sqlite3 is a library that comes built in with Python.
#       (The "import" keyword itself is from CLASS 04: import random)
import sqlite3

# [CLASS 01] a variable holding a string.
# This is the name of the database file. SQLite keeps the WHOLE
# database inside this one file, in the same folder as the app.
DB_NAME = "library.db"


# [CLASS 09] def ... return ---> a function that gives back a result
def get_connection():
    """Open the database file and return the connection to it."""
    # [NEW] sqlite3.connect() opens the file. If the file does not
    #       exist yet, SQLite creates it automatically.
    return sqlite3.connect(DB_NAME)


def create_tables():
    """Create the 3 tables the first time the app runs."""
    conn = get_connection()

    # [NEW] SQL language. "CREATE TABLE IF NOT EXISTS" makes the table
    #       only when it is missing, so it is safe to run every time.
    # [CLASS 02] the SQL is written inside a triple-quoted string.

    # Table 1: one row for every book
    conn.execute("""
        CREATE TABLE IF NOT EXISTS books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title   TEXT NOT NULL,
            author  TEXT NOT NULL
        )
    """)

    # Table 2: one row for every member (Student or Teacher)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS members (
            member_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            member_type TEXT NOT NULL,
            contact     TEXT
        )
    """)

    # Table 3: one row for every time a book is issued.
    # return_date stays EMPTY (NULL) while the book is still out.
    # That single rule tells us which books are issued and overdue.
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            trans_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id     INTEGER NOT NULL,
            member_id   INTEGER NOT NULL,
            issue_date  TEXT NOT NULL,
            due_date    TEXT NOT NULL,
            return_date TEXT,
            fine        INTEGER DEFAULT 0
        )
    """)

    conn.commit()   # [NEW] commit() = save the changes permanently
    conn.close()    # [NEW] close()  = close the file when finished


# [CLASS 09] default argument: values=() is used when nothing is passed
# [CLASS 08] () is an empty tuple
def run_query(sql, values=()):
    """Run a command that CHANGES data (INSERT, UPDATE or DELETE).
    Returns the ID of the new row when the command was an INSERT."""
    conn = get_connection()
    # [NEW] execute(sql, values): the values fill the ? marks in the SQL
    cursor = conn.execute(sql, values)
    conn.commit()
    new_id = cursor.lastrowid   # [NEW] ID that SQLite gave the new row
    conn.close()
    return new_id


def fetch_all(sql, values=()):
    """Run a command that READS data (SELECT).
    Returns a list of tuples, one tuple for each row."""
    conn = get_connection()
    # [NEW] fetchall() collects every row of the answer
    # [CLASS 07 + 08] the answer is a list of tuples, e.g.
    #                 [(1, "Python Basics", "Ali"), (2, "Maths", "Sara")]
    rows = conn.execute(sql, values).fetchall()
    conn.close()
    return rows
