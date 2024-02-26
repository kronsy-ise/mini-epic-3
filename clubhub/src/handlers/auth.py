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

def start_session_for_user(user_id : int):

    cur = db.cursor()
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

def start_session_with_credentials(username : str, password : str):
    """
    We start an auth session 

    Essentially what we do is take the username and password,
    and create a session entry in the database 

    we return the id of this session as a cookie
    this session id is quite sensitive and should be kept private 

    Then this session is provided in the header of each request to identify you 
    from here we can decide what actions you can perform
    """
    cur = db.cursor()

    cur.execute("SELECT user_id,password_hash FROM Users WHERE username = %s", (username,))

    credential = cur.fetchone()


    if credential is None:
        print(f"Username {username} not found in database")  # Log when username is not found
        raise Exception("Invalid Credentials")
    print("Has credential")
    user_id = credential[0]
    password_hash : str = credential[1]
    print("Hash in database:", password_hash)
    password_hash_enc = password_hash.encode("utf-8")

    print(password_hash_enc)
    password_enc = password.encode("utf-8")

    is_valid_pw = bcrypt.checkpw(password_enc, password_hash_enc)
    print(f"Checking password {password} against hash {password_hash}")
    if not is_valid_pw:
        print(f"Password verification failed for username {username}")  # Log when password verification fails
        raise Exception("Invalid Credentials")


    # Now that we know the user has logged in correctly
    # we simply go ahead and create a new session   

    return start_session_for_user(user_id)

@auth_app.get("/login")
def login_page():

    # If you are already logged in 
    # redirect to home
    if util.verify_session() is None:
        
        return render_template("login.html", invalid=False) 
    else:
        return redirect("/")


@auth_app.get("/signup")
def signup_page():
    return render_template("signup.html")

@auth_app.post("/signup")
def signup_action():
    form_data = request.form
    print(form_data)


    username = form_data.get("username")
    password = form_data.get("password")   
    name = form_data.get("name")
    email = form_data.get("email")
    phone = form_data.get("phone")


    print("Signing up as", username, "with password", password, "and name", name, "email", email, "phone", phone)

    password_salt = bcrypt.gensalt()
    password_enc = password.encode("utf-8")
    password_hash = bcrypt.hashpw(password_enc, password_salt).decode("utf-8")

    # Create a new user in the database

    cur = db.cursor()

    cur.execute("""
    INSERT INTO USERS(name, username, email, mobile, password_hash)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING user_id
                   """, (name, username, email, phone, password_hash))
    
    new_user_id = cur.fetchone()
    db.commit()
    
    print("Signed up as user with id", new_user_id)

    # Now that we have signed up, we implicitly log in

    session_secret = start_session_for_user(new_user_id[0])

    res = make_response()
    res.set_cookie("session", session_secret[0], expires=session_secret[1], httponly=True)
    res.status_code = 302
    res.headers.set("Location", "/")
    return res

@auth_app.post("/login")
def login_action():
    print("Logging in")
    username  = request.form.get("username")
    password = request.form.get("password")


    print(f"Attempting to log in as '{username}' with password '{password}'")


    # If the login is correct, set the appropriate cookie and redirect to home 


    try:
        session_secret = start_session_with_credentials(username, password)

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
    except Exception as e:
        print("Exception", e)
        return render_template("login.html", invalid=True)
    


@auth_app.route('/clear-cookies')
def clear_cookies():
    response = make_response(redirect("/"))
    for key in request.cookies.keys():
        response.set_cookie(key, '', max_age=0)
    return response