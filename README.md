# Book Review

book review website. Users will be able to register for website and then log in using their username and password. \
Once they log in, they will be able to search for books, leave reviews for individual books, and see the reviews made by other people. \
This application used a third-party API by Goodreads, another book review website, to pull in ratings from a broader audience. \
Finally, users will be able to query for book details and book reviews programmatically via website’s API.

## images
![Image description](https://i.imgur.com/srrUUdW.png)\
\
![Image description](https://i.imgur.com/uNBBH9B.png)

## List of technologies used:

Python \
Flask \
postgresql \
Jinja2 \
Heroku \
Adminer

## Install all dependencies
$ pip install -r requirements.txt

## ENV Variables

$ export FLASK_APP = application.py # flask run \
$ export DATABASE_URL = Heroku Postgres DB URI \
$ export GOODREADS_KEY = Goodreads API Key. # More info: https://www.goodreads.com/api
