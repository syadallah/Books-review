import os
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
#Session(app)

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
@app.route("/search", methods=["GET"])
