# =====================================================================
#  app.py  --->  FILE 3 of 3 : THE SCREENS (USER INTERFACE)
# ---------------------------------------------------------------------
#  Job of this file: draw the web pages with Streamlit.
#  It takes input from the librarian, calls logic.py, shows the result.
#
#  To run the app, type this in the terminal:
#       streamlit run app.py
#
#  IMPORTANT: Streamlit runs this whole file again from top to bottom
#  every time the librarian clicks or types something.
#
#  How to read the tags in the comments:
#     [CLASS 09]  ---> taught in that class notebook
#     [NEW]       ---> not taught yet, added with the help of AI
# =====================================================================

from datetime import date    # [NEW] datetime library

# [NEW] two outside libraries. [CLASS 12] "import ... as ..." gives a
#       short name, same style as: import numpy as np
import streamlit as st
import pandas as pd

# [NEW] our own two files
import database
import logic


# ---------------------------------------------------------------------
#  SETUP (runs on every rerun)
# ---------------------------------------------------------------------
# [NEW] title and layout of the browser tab
st.set_page_config(page_title="Library Management System", layout="wide")

# Make sure the database file and its 3 tables exist
database.create_tables()

# [NEW] st.session_state is Streamlit's memory. It works like a
#       dictionary [CLASS 08/09] and keeps its values between reruns.
#       Normal variables are forgotten on every rerun.
if "logged_in" not in st.session_state:      # [CLASS 03] not in
    st.session_state["logged_in"] = False


# ---------------------------------------------------------------------
#  SMALL HELPER FUNCTIONS
# ---------------------------------------------------------------------
# [CLASS 09] functions
def save_message_and_refresh(result):
    """Keep the (success, message) result in memory, then redraw the
    page so every table shows the newest data."""
    st.session_state["message"] = result
    st.rerun()      # [NEW] run the file again from the top, right now


def show_saved_message():
    """Show the message kept by the function above, one time only."""
    if "message" in st.session_state:
        # [CLASS 01] two variables from one tuple
        success, text = st.session_state["message"]
        if success:
            st.success(text)    # [NEW] green box
        else:
            st.error(text)      # [NEW] red box
        del st.session_state["message"]   # [CLASS 09] delete a key


def show_table(records, empty_text):
    """Show a list of dictionaries as a table."""
    if len(records) == 0:
        st.info(empty_text)     # [NEW] blue information box
    else:
        # [NEW] pandas DataFrame = a table made from our list of
        #       dictionaries. st.dataframe() draws it on the page.
        st.dataframe(pd.DataFrame(records), hide_index=True)


def get_id(choice):
    """The dropdown text looks like '3 - Python Basics'.
    Take the number before the dash and return it as an int."""
    # [CLASS 06] split()   [CLASS 07] indexing   [CLASS 02] int()
    return int(choice.split(" - ")[0])


# ---------------------------------------------------------------------
#  PAGE: LOGIN
# ---------------------------------------------------------------------
def login_page():
    st.title("Library Management System")
    st.subheader("Librarian Login")

    # [NEW] a form groups input boxes with one submit button
    # [CLASS 10] form is an object, and we call its methods with a dot
    form = st.form("login_form")
    username = form.text_input("Username")
    password = form.text_input("Password", type="password")
    submitted = form.form_submit_button("Login")

    # [CLASS 03] if / else. submitted is True only on the click
    if submitted:
        if logic.check_login(username, password):
            st.session_state["logged_in"] = True
            st.rerun()
        else:
            st.error("Wrong username or password.")


# ---------------------------------------------------------------------
#  PAGE: DASHBOARD
# ---------------------------------------------------------------------
def dashboard_page():
    st.title("Dashboard")
    stats = logic.get_stats()     # a dictionary of numbers

    # [NEW] st.columns(3) makes 3 side-by-side columns
    # [CLASS 01] three variables get their values in one line
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Books", stats["Total Books"])   # [NEW] number card
    col2.metric("Available", stats["Available"])
    col3.metric("Issued", stats["Issued"])

    col4, col5, col6 = st.columns(3)
    col4.metric("Members", stats["Members"])
    col5.metric("Overdue Books", stats["Overdue"])
    col6.metric("Fines Collected", f"Rs. {stats['Fines Collected']}")

    st.subheader("Books: Available vs Issued")
    # [NEW] a small pandas table, then a bar chart from it
    chart_data = pd.DataFrame({
        "Status": ["Available", "Issued"],
        "Books": [stats["Available"], stats["Issued"]]})
    st.bar_chart(chart_data, x="Status", y="Books")

    st.caption(f"Rules: every book is issued for {logic.LOAN_DAYS} days. "
               f"Fine is Rs. {logic.FINE_PER_DAY} per late day. "
               "Students may borrow 3 books, Teachers 5.")


# ---------------------------------------------------------------------
#  PAGE: BOOKS  (add, delete, search)
# ---------------------------------------------------------------------
def books_page():
    st.title("Books")
    show_saved_message()

    # ----- Add a book -----
    st.subheader("Add a Book")
    form = st.form("add_book_form", clear_on_submit=True)
    title = form.text_input("Title")
    author = form.text_input("Author")
    if form.form_submit_button("Add Book"):
        save_message_and_refresh(logic.add_book(title, author))

    # ----- Delete a book -----
    st.subheader("Delete a Book")
    all_books = logic.search_books()
    if len(all_books) == 0:
        st.info("No books to delete.")
    else:
        # [CLASS 07] build a list of choices with a for loop
        choices = []
        for book in all_books:
            choices.append(f"{book['Book ID']} - {book['Title']} "
                           f"by {book['Author']} ({book['Status']})")

        # [NEW] selectbox = dropdown list
        choice = st.selectbox("Choose the book to delete", choices)
        if st.button("Delete Book"):          # [NEW] a button
            save_message_and_refresh(logic.delete_book(get_id(choice)))

    # ----- Search books -----
    st.subheader("Search Books")
    keyword = st.text_input("Type a title or an author "
                            "(leave empty to see all books)")
    results = logic.search_books(keyword)
    st.write(f"{len(results)} book(s) found.")     # [NEW] st.write
    show_table(results, "No book matches your search.")


# ---------------------------------------------------------------------
#  PAGE: MEMBERS  (register, list)
# ---------------------------------------------------------------------
def members_page():
    st.title("Members")
    show_saved_message()

    st.subheader("Register a Member")
    form = st.form("member_form", clear_on_submit=True)
    name = form.text_input("Name")
    member_type = form.selectbox("Member type", ["Student", "Teacher"])
    contact = form.text_input("Contact (phone or email)")
    if form.form_submit_button("Register Member"):
        save_message_and_refresh(
            logic.register_member(name, member_type, contact))

    st.subheader("All Members")
    show_table(logic.get_all_members(), "No members registered yet.")


# ---------------------------------------------------------------------
#  PAGE: ISSUE BOOK
# ---------------------------------------------------------------------
def issue_page():
    st.title("Issue a Book")
    show_saved_message()

    members = logic.get_all_members()

    # Only books that are Available can be issued
    available_books = []
    for book in logic.search_books():
        if book["Status"] == "Available":
            available_books.append(book)

    # [CLASS 03] if / elif / else
    if len(members) == 0:
        st.info("Register a member first (Members page).")
    elif len(available_books) == 0:
        st.info("No book is available to issue right now.")
    else:
        member_choices = []
        for member in members:
            member_choices.append(
                f"{member['Member ID']} - {member['Name']} ({member['Type']}) "
                f"- has {member['Books Borrowed']} of {member['Borrow Limit']}")

        book_choices = []
        for book in available_books:
            book_choices.append(
                f"{book['Book ID']} - {book['Title']} by {book['Author']}")

        member_choice = st.selectbox("Member", member_choices)
        book_choice = st.selectbox("Book", book_choices)

        # [NEW] date picker. Today is the default. An older date can be
        #       chosen to enter a past issue (useful to test the fine).
        issue_date = st.date_input("Issue date", value=date.today(),
                                   max_value=date.today())

        if st.button("Issue Book"):
            # [CLASS 09] keyword argument: issue_date=issue_date
            result = logic.issue_book(get_id(book_choice),
                                      get_id(member_choice),
                                      issue_date=issue_date)
            save_message_and_refresh(result)

    st.subheader("Books Issued Right Now")
    show_table(logic.get_active_loans(), "No book is issued right now.")


# ---------------------------------------------------------------------
#  PAGE: RETURN BOOK
# ---------------------------------------------------------------------
def return_page():
    st.title("Return a Book")
    show_saved_message()

    loans = logic.get_active_loans()

    if len(loans) == 0:
        st.info("No book is issued right now.")
    else:
        loan_choices = []
        for loan in loans:
            loan_choices.append(
                f"{loan['Loan ID']} - {loan['Book']} - {loan['Member']} "
                f"(due {loan['Due Date']})")

        choice = st.selectbox("Choose the loan to return", loan_choices)
        loan_id = get_id(choice)

        # Find the chosen loan to show its fine before returning
        for loan in loans:
            if loan["Loan ID"] == loan_id:
                if loan["Days Late"] > 0:
                    st.warning(f"This book is {loan['Days Late']} day(s) "
                               f"late. Fine: Rs. {loan['Fine So Far (Rs.)']}")
                else:
                    st.success("This book is on time. No fine.")

        if st.button("Return Book"):
            save_message_and_refresh(logic.return_book(loan_id))

        st.subheader("Books Issued Right Now")
        show_table(loans, "No book is issued right now.")


# ---------------------------------------------------------------------
#  PAGE: OVERDUE BOOKS
# ---------------------------------------------------------------------
def overdue_page():
    st.title("Overdue Books")
    overdue = logic.get_overdue_loans()

    # [CLASS 05] running total with a for loop
    total_fine = 0
    for loan in overdue:
        total_fine = total_fine + loan["Fine So Far (Rs.)"]

    col1, col2 = st.columns(2)
    col1.metric("Overdue Books", len(overdue))
    col2.metric("Total Fine Due", f"Rs. {total_fine}")

    show_table(overdue, "No overdue books.")


# ---------------------------------------------------------------------
#  PAGE: HISTORY
# ---------------------------------------------------------------------
def history_page():
    st.title("Return History")
    show_table(logic.get_history(), "No book has been returned yet.")


# ---------------------------------------------------------------------
#  MAIN PART: decide which page to show
# ---------------------------------------------------------------------
if st.session_state["logged_in"] == False:
    login_page()
else:
    # [NEW] st.sidebar = the menu panel on the left side
    st.sidebar.title("Library Menu")

    # [NEW] radio = choose one option from a list [CLASS 07]
    page = st.sidebar.radio("Go to", ["Dashboard", "Books", "Members",
                                      "Issue Book", "Return Book",
                                      "Overdue Books", "History"])

    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.rerun()

    # [CLASS 03] if / elif / else chooses the page function to call
    if page == "Dashboard":
        dashboard_page()
    elif page == "Books":
        books_page()
    elif page == "Members":
        members_page()
    elif page == "Issue Book":
        issue_page()
    elif page == "Return Book":
        return_page()
    elif page == "Overdue Books":
        overdue_page()
    else:
        history_page()
