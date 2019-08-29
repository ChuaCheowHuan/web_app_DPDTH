import csv
import flask
import os

from flask import Flask, redirect, render_template, request, url_for, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine("sqlite:///data.db")
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    if session.get("username"):
        return render_template("user.html", username=session["username"])
    else:
        return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    user = db.execute("SELECT * FROM users WHERE (username = '" + username + "') AND (password = '" + password + "')").first()
    if user:
        session["username"] = user.username
        return redirect(url_for("index"))
    return render_template("login.html", invalid=True)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))
