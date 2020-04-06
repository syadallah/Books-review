import os, json
import requests

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

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
