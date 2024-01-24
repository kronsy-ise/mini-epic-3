from __future__ import annotations
from flask import Blueprint, make_response, request, render_template, session, redirect
from globals import db
from models.user import User
from models.user import UserKind
import bcrypt
import psycopg2.errors as pgerrors
import random
import datetime
import util
from models.user import User

auth_app = Blueprint('auth_app', __name__)


SESSION_ID_VALID_CHARS="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._+=/$%^"

def start_session(username : str, password : str):
    """
    We start an auth session 

    Essentially what we do is take the username and password,
    and create a session entry in the database 

    we return the id of this session as a cookie
    this session id is quite sensitive and should be kept private 

    Then this session is is provided in the header of each request to identify you 
    from here we can decide what actions you can perform
    """
    cur = db.cursor()

    cur.execute("SELECT id,password_hash FROM Users WHERE username = %s", (username,))

    credential = cur.fetchone()


    if credential is None:
        raise Exception("Invalid Credentials")
    print("Has credential")
    user_id = credential[0]
    password_hash : str = credential[1]

    password_hash_enc = password_hash.encode("utf-8")

    print(password_hash_enc)
    password_enc = password.encode("utf-8")

    is_valid_pw = bcrypt.checkpw(password_enc, password_hash_enc)

    if not is_valid_pw:
        raise Exception("Invalid Credentials")


    # Now that we know the user has logged in correctly
    # we simply go ahead and create a new session
   
    session_secret = ""

    # Generate the session id
    for _ in range(36):
        c = random.choice(SESSION_ID_VALID_CHARS)
        session_secret += c

    now = datetime.datetime.now()

    expiry = now + datetime.timedelta(hours=6)



    cur.execute("""
    INSERT INTO Sessions(secret, user_id, expires_at) 
    VALUES
    (%s, %s, %s)
    """, (session_secret, user_id, expiry))


    db.commit()


    return (session_secret, expiry)

@auth_app.get("/login")
def login_page():

    # If you are already logged in 
    # redirect to home
    if util.verify_session() is None:
        
        return render_template("login.html", invalid=False) 
    else:
        return redirect("/")


@auth_app.post("/login")
def login_action():
    print("Logging in")
    username  = request.form.get("username")
    password = request.form.get("password")


    print(f"Attempting to log in as '{username}' with password '{password}'")


    # If the login is correct, set the appropriate cookie and redirect to home 

    session_secret = start_session(username, password)
    print(session_secret)

    # When the login is wrong, return the login page 
    # with an error message
    if session_secret is None:
        return render_template("login.html", invalid=True)
    else:
        res = make_response()
        res.set_cookie("session", session_secret[0], expires=session_secret[1], httponly=True)
        res.status_code = 302
        res.headers.set("Location", "/")
        return res
