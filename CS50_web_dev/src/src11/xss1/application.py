import csv
import flask
import os

from flask import Flask, redirect, render_template, request, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Set up database
engine = create_engine("sqlite:///data.db")
db = scoped_session(sessionmaker(bind=engine))

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        contents = request.form.get("contents")
        db.execute("INSERT INTO messages (contents) VALUES (:contents)", {"contents": contents})
    messages = db.execute("SELECT * FROM messages").fetchall()
    return render_template("index.html", messages=messages)

