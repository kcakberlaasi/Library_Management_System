# =====================================================================
#  logic.py  --->  FILE 2 of 3 : THE LIBRARY RULES
# ---------------------------------------------------------------------
#  Job of this file: all the rules of the library.
#  (borrow limit, due date, fine, overdue, login check)
#  It asks database.py to save and read data. It draws no screen.
#
#  How to read the tags in the comments:
#     [CLASS 09]  ---> taught in that class notebook
#     [NEW]       ---> not taught yet, added with the help of AI
# =====================================================================

# [CLASS 11] "from ... import ..." (same style as: from abc import ABC)
# [NEW] the datetime library: "date" is a calendar date,
#       "timedelta" is a number of days we can add to a date.
from datetime import date, timedelta

# [NEW] importing OUR OWN file. database.py becomes a module, and we
#       call its functions as database.fetch_all(...) etc.
import database


# ---------------------------------------------------------------------
#  SETTINGS  (change the rules of the library here, in one place)
# ---------------------------------------------------------------------
# [CLASS 01] variables
LOAN_DAYS = 7              # a book must come back within 7 days
FINE_PER_DAY = 10          # Rs. 10 for every late day
ADMIN_USERNAME = "admin"   # librarian login
ADMIN_PASSWORD = "admin123"


# ---------------------------------------------------------------------
#  MEMBER CLASSES  (OOP)
# ---------------------------------------------------------------------
# [CLASS 10] class, __init__, self, methods
class Member:
    """Parent class: what every member has."""

    def __init__(self, name, contact):
        self.name = name
        self.contact = contact
        self.member_type = "Member"

    def borrow_limit(self):
        return 0


# [CLASS 11] Inheritance: Student is a child class of Member
class Student(Member):

    def __init__(self, name, contact):
        # [CLASS 11] super() calls the __init__ of the parent class
        super().__init__(name, contact)
        self.member_type = "Student"

    # [CLASS 11] Polymorphism: same method name, different behaviour
    def borrow_limit(self):
        return 3


class Teacher(Member):

    def __init__(self, name, contact):
        super().__init__(name, contact)
        self.member_type = "Teacher"

    def borrow_limit(self):
        return 5


# [CLASS 09] function with default arguments
def make_member(member_type, name="", contact=""):
    """Create the correct object (Student or Teacher)."""
    # [CLASS 03] if / else
    if member_type == "Teacher":
        return Teacher(name, contact)
    else:
        return Student(name, contact)


# ---------------------------------------------------------------------
#  LOGIN
# ---------------------------------------------------------------------
def check_login(username, password):
    """Return True when the librarian's username and password match."""
    # [CLASS 04] nested if, same idea as the "user login" program
    if username == ADMIN_USERNAME:
        if password == ADMIN_PASSWORD:
            return True
    return False


# ---------------------------------------------------------------------
#  BOOKS
# ---------------------------------------------------------------------
def get_issued_book_ids():
    """Return a list of the IDs of all books that are out right now."""
    # [NEW] SQL: SELECT reads rows. "return_date IS NULL" means the
    #       book has not come back yet.
    rows = database.fetch_all(
        "SELECT book_id FROM transactions WHERE return_date IS NULL")

    # [CLASS 07] empty list + for loop + append
    issued_ids = []
    for row in rows:
        issued_ids.append(row[0])   # [CLASS 08] indexing a tuple
    return issued_ids


def add_book(title, author):
    """Add one book. Returns (success, message)."""
    # [CLASS 06] strip() removes extra spaces, title() capitalises
    title = title.strip().title()
    author = author.strip().title()

    # [CLASS 03] if with the "or" logical operator
    if title == "" or author == "":
        # [CLASS 08] returning a tuple: (True/False, message)
        return (False, "Please enter both the title and the author.")

    # [NEW] SQL: INSERT adds a new row. Each ? is filled from the tuple.
    #       Using ? (not an f-string) keeps the database safe from
    #       harmful text typed by a user.
    new_id = database.run_query(
        "INSERT INTO books (title, author) VALUES (?, ?)", (title, author))

    # [CLASS 02] f-string
    return (True, f"Book '{title}' added with Book ID {new_id}.")


def search_books(keyword=""):
    """Search books by title OR author. An empty keyword returns all
    books. Returns a list of dictionaries."""
    # [CLASS 06] string concatenation with +
    # [NEW] in SQL, % means "any text", so %ali% finds "ali" anywhere
    pattern = "%" + keyword.strip() + "%"

    # [NEW] SQL: WHERE filters rows, LIKE compares text with a pattern,
    #       ORDER BY sorts the answer.
    rows = database.fetch_all(
        """SELECT book_id, title, author FROM books
           WHERE title LIKE ? OR author LIKE ?
           ORDER BY title""",
        (pattern, pattern))

    issued_ids = get_issued_book_ids()

    books = []
    for row in rows:
        # [CLASS 01] giving several variables their values in one line
        book_id, title, author = row

        # [CLASS 03] membership operator "in"
        if book_id in issued_ids:
            status = "Issued"
        else:
            status = "Available"

        # [CLASS 08/09] a dictionary for each book, kept in a list
        books.append({"Book ID": book_id, "Title": title,
                      "Author": author, "Status": status})
    return books


def delete_book(book_id):
    """Delete a book. A book that is issued cannot be deleted."""
    if book_id in get_issued_book_ids():
        return (False, "This book is issued right now. "
                       "Return it first, then delete it.")

    # [NEW] SQL: DELETE removes the row. (book_id,) is a tuple with
    #       one item [CLASS 08: the comma makes it a tuple]
    database.run_query("DELETE FROM books WHERE book_id = ?", (book_id,))
    return (True, f"Book ID {book_id} deleted.")


# ---------------------------------------------------------------------
#  MEMBERS
# ---------------------------------------------------------------------
def register_member(name, member_type, contact=""):
    """Register a Student or a Teacher. Returns (success, message)."""
    name = name.strip().title()
    contact = contact.strip()

    if name == "":
        return (False, "Please enter the member's name.")

    # [CLASS 10] creating an object from a class
    member = make_member(member_type, name, contact)

    new_id = database.run_query(
        "INSERT INTO members (name, member_type, contact) VALUES (?, ?, ?)",
        (member.name, member.member_type, member.contact))

    return (True, f"{member.member_type} '{member.name}' registered with "
                  f"Member ID {new_id}. Borrow limit: "
                  f"{member.borrow_limit()} books.")


def count_active_loans(member_id):
    """How many books does this member have right now?"""
    rows = database.fetch_all(
        """SELECT trans_id FROM transactions
           WHERE member_id = ? AND return_date IS NULL""",
        (member_id,))
    return len(rows)    # [CLASS 07] len() of a list


def get_all_members():
    """Return a list of dictionaries, one for each member."""
    rows = database.fetch_all(
        """SELECT member_id, name, member_type, contact
           FROM members ORDER BY name""")

    members = []
    for row in rows:
        member_id, name, member_type, contact = row
        member = make_member(member_type, name, contact)
        members.append({"Member ID": member_id,
                        "Name": name,
                        "Type": member_type,
                        "Contact": contact,
                        "Books Borrowed": count_active_loans(member_id),
                        "Borrow Limit": member.borrow_limit()})
    return members


# ---------------------------------------------------------------------
#  DUE DATE AND FINE
# ---------------------------------------------------------------------
def calculate_late_days(due_date, check_date):
    """How many days after the due date is check_date? Never below 0."""
    # [NEW] subtracting two dates gives the gap; .days is the number
    late_days = (check_date - due_date).days

    if late_days < 0:       # returned early: not late at all
        late_days = 0
    return late_days


def calculate_fine(due_date, check_date):
    """Fine = late days x fine per day."""
    # [CLASS 02] arithmetic operator *
    return calculate_late_days(due_date, check_date) * FINE_PER_DAY


# ---------------------------------------------------------------------
#  ISSUE AND RETURN
# ---------------------------------------------------------------------
def issue_book(book_id, member_id, issue_date=None):
    """Issue a book to a member. Returns (success, message)."""
    # Check 1: does the member exist?
    member_rows = database.fetch_all(
        "SELECT name, member_type FROM members WHERE member_id = ?",
        (member_id,))
    if len(member_rows) == 0:
        return (False, "Member not found.")
    name, member_type = member_rows[0]

    # Check 2: does the book exist?
    book_rows = database.fetch_all(
        "SELECT title FROM books WHERE book_id = ?", (book_id,))
    if len(book_rows) == 0:
        return (False, "Book not found.")
    title = book_rows[0][0]   # [CLASS 07] indexing: first row, first item

    # Check 3: is the book free?
    if book_id in get_issued_book_ids():
        return (False, f"'{title}' is already issued to someone.")

    # Check 4: borrow limit (Student 3, Teacher 5)
    member = make_member(member_type, name)
    borrowed = count_active_loans(member_id)
    # [CLASS 02] comparison operator >=
    if borrowed >= member.borrow_limit():
        return (False, f"{name} ({member_type}) already has {borrowed} "
                       f"books. The limit is {member.borrow_limit()}.")

    # [CLASS 03] identity operator "is"   [NEW] date.today() = today
    if issue_date is None:
        issue_date = date.today()

    # [NEW] timedelta(days=7) is "7 days"; date + 7 days = the due date
    due_date = issue_date + timedelta(days=LOAN_DAYS)

    # [NEW] isoformat() turns a date into text like "2026-11-11" so it
    #       can be stored in the database.
    database.run_query(
        """INSERT INTO transactions (book_id, member_id, issue_date, due_date)
           VALUES (?, ?, ?, ?)""",
        (book_id, member_id, issue_date.isoformat(), due_date.isoformat()))

    return (True, f"'{title}' issued to {name}. Due date: {due_date}.")


def return_book(trans_id, return_date=None):
    """Return a book and calculate the fine. Returns (success, message)."""
    rows = database.fetch_all(
        """SELECT due_date FROM transactions
           WHERE trans_id = ? AND return_date IS NULL""",
        (trans_id,))
    if len(rows) == 0:
        return (False, "This loan was not found or is already returned.")

    # [NEW] fromisoformat() turns the stored text back into a date
    due_date = date.fromisoformat(rows[0][0])

    if return_date is None:
        return_date = date.today()

    fine = calculate_fine(due_date, return_date)

    # [NEW] SQL: UPDATE changes an existing row
    database.run_query(
        "UPDATE transactions SET return_date = ?, fine = ? WHERE trans_id = ?",
        (return_date.isoformat(), fine, trans_id))

    if fine > 0:
        late_days = calculate_late_days(due_date, return_date)
        return (True, f"Book returned {late_days} day(s) late. "
                      f"Fine to collect: Rs. {fine}.")
    else:
        return (True, "Book returned on time. No fine.")


# ---------------------------------------------------------------------
#  LISTS FOR THE SCREENS
# ---------------------------------------------------------------------
def get_book_titles():
    """Return a dictionary:  book_id ---> title"""
    rows = database.fetch_all("SELECT book_id, title FROM books")
    titles = {}                       # [CLASS 08] empty dictionary
    for row in rows:
        titles[row[0]] = row[1]       # [CLASS 09] add key : value
    return titles


def get_member_details():
    """Return a dictionary:  member_id ---> {"name": .., "type": ..}"""
    rows = database.fetch_all(
        "SELECT member_id, name, member_type FROM members")
    details = {}
    for row in rows:
        # [CLASS 08] a dictionary inside a dictionary
        details[row[0]] = {"name": row[1], "type": row[2]}
    return details


def get_active_loans():
    """All books that are out right now, with the fine so far."""
    rows = database.fetch_all(
        """SELECT trans_id, book_id, member_id, issue_date, due_date
           FROM transactions WHERE return_date IS NULL
           ORDER BY due_date""")

    titles = get_book_titles()
    members = get_member_details()
    today = date.today()

    loans = []
    for row in rows:
        trans_id, book_id, member_id, issue_date, due_date = row
        due = date.fromisoformat(due_date)

        # [CLASS 09] reading values from a dictionary by key
        loans.append({"Loan ID": trans_id,
                      "Book": titles[book_id],
                      "Member": members[member_id]["name"],
                      "Type": members[member_id]["type"],
                      "Issue Date": issue_date,
                      "Due Date": due_date,
                      "Days Late": calculate_late_days(due, today),
                      "Fine So Far (Rs.)": calculate_fine(due, today)})
    return loans


def get_overdue_loans():
    """Only the loans whose due date has passed."""
    overdue = []
    for loan in get_active_loans():
        if loan["Days Late"] > 0:
            overdue.append(loan)
    return overdue


def get_history():
    """All books that were returned, newest first."""
    rows = database.fetch_all(
        """SELECT trans_id, book_id, member_id, issue_date, due_date,
                  return_date, fine
           FROM transactions WHERE return_date IS NOT NULL
           ORDER BY return_date DESC, trans_id DESC""")

    titles = get_book_titles()
    members = get_member_details()

    history = []
    for row in rows:
        trans_id, book_id, member_id, issue_date, due_date, return_date, fine = row

        # A returned book may have been deleted from the catalogue later
        if book_id in titles:           # [CLASS 09] "in" searches the keys
            title = titles[book_id]
        else:
            title = "(deleted book)"

        history.append({"Loan ID": trans_id,
                        "Book": title,
                        "Member": members[member_id]["name"],
                        "Issue Date": issue_date,
                        "Due Date": due_date,
                        "Return Date": return_date,
                        "Fine (Rs.)": fine})
    return history


def get_stats():
    """Numbers for the dashboard, returned as one dictionary."""
    total_books = len(search_books())
    issued = len(get_issued_book_ids())

    # [CLASS 05] running total with a for loop
    fines_collected = 0
    for record in get_history():
        fines_collected = fines_collected + record["Fine (Rs.)"]

    return {"Total Books": total_books,
            "Available": total_books - issued,
            "Issued": issued,
            "Members": len(get_all_members()),
            "Overdue": len(get_overdue_loans()),
            "Fines Collected": fines_collected}
