import os, json
import requests

from flask import Flask, session, redirect, render_template, request, jsonify, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from cachelib.file import FileSystemCache
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
# database engine object from SQLAlchemy that manages connections to the database

engine = create_engine(os.getenv("DATABASE_URL"))
# create a 'scoped session' that ensures different users' interactions with the
# database are kept separate
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():

    return render_template('index.html')
    #res=requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "5fI1wLvZOj028LGUwMrLdQ",
    #                                                                                 "isbns": "1632168146"}).json()
    #print(res)
    #return res

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    username = request.form.get("username")
    # Redirect user to home page
    return redirect("/")
            # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("error.html", message="must provide username")
                  # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("error.html", message="must provide password")

        # Query database for username (http://zetcode.com/db/sqlalchemy/rawsql/)
        # https://docs.sqlalchemy.org/en/latest/core/connections.html#sqlalchemy.engine.ResultProxy
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                            {"username": username})

        result = rows.fetchone()

        # Ensure username exists and password is correct
        if result == None or not check_password_hash(result[2], request.form.get("password")):
            return render_template("error.html", message="invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = result[0]
        session["user_name"] = result[1]

        # Redirect user to home page
        return redirect("/")


    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
@app.route("/register", methods=["GET", "POST"])
def register():
     # Forget any user_id
    session.clear()
 # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("error.html", message="must provide username")
       # Query database for username
        userCheck = db.execute("SELECT * FROM users WHERE username = :username",
                          {"username":request.form.get("username")}).fetchone()
                            # Check if username already exist
        if userCheck:
            return render_template("error.html", message="username already exist")
         # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("error.html", message="must provide password")

        # Ensure confirmation wass submitted
        elif not request.form.get("confirmation"):
            return render_template("error.html", message="must confirm password")

        # Check passwords are equal
        elif not request.form.get("password") == request.form.get("confirmation"):
            return render_template("error.html", message="passwords didn't match")

               # Hash user's password to store in DB
        hashedPassword = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)

        # Insert register into DB
        db.execute("INSERT INTO users (username, hash) VALUES (:username, :password)",
                            {"username":request.form.get("username"),
                             "password":hashedPassword})

        # Commit changes to database
        db.commit()

        flash('Account created', 'info')

        # Redirect user to login page
        return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/search", methods=["GET"])
def search():
# if no book provided in the search bar return error
    if not request.args.get("book"):
        return render_template("error.html", message="you must provide a book.")
        #   Take input
        query = "%" + request.args.get("book") + "%"
        # make select from datbase where isbn, title, or author provided
        rows = db.execute("SELECT isbn, title, author, year FROM books WHERE \
                        isbn LIKE :query OR \
                        title LIKE :query OR \
                        author LIKE :query LIMIT 15",
                        {"query": query})
          # Books not founded
    if rows.rowcount == 0:
        return render_template("error.html", message="we can't find books with that description.")

    # Fetch all the results
    books = rows.fetchall()

    return render_template("results.html", books=books)

@app.route("/book/<isbn>", methods=['GET','POST'])
@login_required
def book(isbn):

    if request.method == "POST":

        # Save current user info
        currentUser = session["user_id"]

        # Fetch form data
        rating = request.form.get("rating")
        comment = request.form.get("comment")

        # Search book_id by ISBN
        row = db.execute("SELECT id FROM books WHERE isbn = :isbn",
                        {"isbn": isbn})
                        # Save id into variable
        bookId = row.fetchone() # (id,)
        bookId = bookId[0]
        # Check for user submission (ONLY 1 review/user allowed per book)
        row2 = db.execute("SELECT * FROM reviews WHERE user_id = :user_id AND book_id = :book_id",
                    {"user_id": currentUser,
                     "book_id": bookId})
