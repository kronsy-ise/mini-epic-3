from __future__ import annotations
from typing import Optional
from flask import Flask, request, request_finished, session, make_response
import psycopg2
from psycopg2 import errors as pgerrors
import util
import random
import bcrypt
import datetime
from enum import Enum
config = util.load_configuration()
db = util.open_database(config["DATABASE_URL"])


app = Flask(__name__)

SESSION_ID_VALID_CHARS="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._+=/$%^"

class UserKind(Enum):
    Unapproved = "unapproved"
    Coordinator = "coordinator"
    User = "user"

    @staticmethod 
    def from_str(s : str) -> UserKind:
        if s == "unapproved": return UserKind.Unapproved
        elif s == "coordinator": return UserKind.Coordinator
        elif s == "user": return UserKind.User
        
        raise Exception("Unknown kind")

class User:
    username : str 
    name : str 
    is_admin : bool
    kind : UserKind

    def __init__(self, username, name, is_admin, kind) -> None:
        self.username = username
        self.name = name 
        self.is_admin = is_admin
        self.kind = kind

    def __repr__(self) -> str:
        return f"User {self.name} <{self.username}> {'admin' if self.is_admin else ''} kind={self.kind}"

    @staticmethod
    def fetch(id : int) -> Optional[User]:

        cur = db.cursor()

        cur.execute("SELECT username, name, is_admin, user_kind FROM Users WHERE id = %s", (id,))
        entry = cur.fetchone()

        if entry == None:
            return None 
        else:
            return User(entry[0], entry[1], entry[2], UserKind.from_str(entry[3]))
            


def verify_session() -> Optional[User]:
    
    session_secret = request.cookies.get("session")
    if session_secret is None:
        return None
    cur = db.cursor()

    cur.execute("SELECT user_id, expires_at FROM Sessions WHERE expires_at > NOW() AND secret = %s", (session_secret, ))

    session = cur.fetchone()

    user_id : int = session[0]

    user = User.fetch(user_id)

    return user



@app.get("/api/users")
def get_all_users():
    # TODO: Add auth
    user = verify_session()

    if user is None:
        return "Authorization is required to view all users", 403
    elif user.kind == UserKind.User:
        return "Normal users may only view their own profile", 403
    elif user.kind == UserKind.Coordinator and not user.is_admin:
        return "You may only view members of your clubs, please check users via GET /api/clubs/<id>/members", 403

    cur = db.cursor()
    cur.execute("""
    SELECT username, email, mobile, is_admin, user_kind, id FROM Users
    """)
    users = cur.fetchall()

    response = []

    for user in users:
        username = user[0]
        email = user[1]
        mobile = user[2]
        is_admin = user[3]
        kind = user[4]
        id = user[5]

        response.append({
            "username" : username,
            "email" : email,
            "mobile" : mobile,
            "is_admin" : is_admin,
            "kind" : kind,
            "id" : id
        })

    print(response)
    return response

@app.post("/api/users/<id>/approve")
def approve_user(id):


    auth_user = verify_session()

    if auth_user is None:
        return "Unauthorized to perform action", 403 
    elif not auth_user.is_admin:
        return "Admin access required to perform action", 403

    data = request.json

    if data is None:
        return "Expected Body", 400

    user_kind = data["kind"]

    if user_kind != "user" and user_kind != "coordinator":
        return "Invalid user type, expected 'user' or 'coordinator'", 400


    cur = db.cursor()

    cur.execute("""
    SELECT user_kind FROM Users WHERE id = %s
    """, (id))

    user = cur.fetchone()
    
    if user == None:
        return "User Not Found", 404

    current_kind = user[0]

    if current_kind != "unapproved":
        return "User already approved", 400

    cur.execute("""
    UPDATE Users 
        SET user_kind = %s 
    WHERE id = %s
    """, (user_kind, id))

    db.commit()

    return "Approved as " + user_kind, 200


@app.post("/api/auth")
def start_session():
    """
    We start an auth session 

    Essentially what we do is take the username and password,
    and create a session entry in the database 

    we return the id of this session as a cookie
    this session id is quite sensitive and should be kept private 

    Then this session is is provided in the header of each request to identify you 
    from here we can decide what actions you can perform
    """

    print("Incoming Request")

    data = request.json

    if data is None:
        return "Expected Body", 400

    username : str = data["username"]
    password : str = data["password"]

    print("AA")
    cur = db.cursor()

    print("Got cursor")
    print("uname", username)
    cur.execute("SELECT id,password_hash FROM Users WHERE username = %s", (username,))

    print("Exec")
    credential = cur.fetchone()



    if credential is None:
        return "User with username Not Found", 404
    print("Has credential")
    user_id = credential[0]
    password_hash : str = credential[1]

    password_hash_enc = password_hash.encode("utf-8")

    print(password_hash_enc)
    password_enc = password.encode("utf-8")

    is_valid_pw = bcrypt.checkpw(password_enc, password_hash_enc)

    if not is_valid_pw:
        return "Mismatched password", 403


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

    res = make_response()

    res.set_data("Session started successfully")
    res.status = 200
    res.set_cookie("session", session_secret, expires=expiry, httponly=True)

    db.commit()


    return res


# @app.patch("/api/users/<user_id>")
# def update_user(id):
#     data = request.json
#
#     if data is None:
#         return "Expected Body", 400
#
#     username = data["username"]
#     email = data["email"]
#     mobile = data["mobile"]
#     password : str = data["password"]
#
#     password_bytes = password.encode("utf-8")
#     password_salt = bcrypt.gensalt()
#     password_hash = bcrypt.hashpw(password_bytes, password_salt)

@app.post("/api/users")
def create_user():
    data = request.json

    if data is None:
        return "Expected Body", 400

    username = data["username"]
    name = data["name"]
    email = data["email"]
    mobile = data["mobile"]
    password : str = data["password"]

    password_bytes = password.encode("utf-8")
    password_salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password_bytes, password_salt)

    print(f"Create user {username} <{email} | {mobile}>")
    print(f"Bcrypt Hash: {password_hash}")

    cur = db.cursor()

    cur.execute("""
    SELECT COUNT(id) FROM Users
    """)

    user_count : int = cur.fetchone()[0]

    # When this is the first user, implicitly make this the super-admin account
    # TODO: Make this an sql rule
    is_admin = user_count == 0
    kind = "coordinator" if is_admin else "unapproved"

    print(f"User count: {user_count}")

    try:
    # Create the user
        cur.execute("""
    INSERT INTO Users(username, name, email, mobile, password_hash, is_admin, user_kind)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (username, name, email, mobile, password_hash.decode("utf-8"), is_admin, kind))
   
        db.commit()

        return "Successfully created user, waiting admin approval", 201
    
    except pgerrors.UniqueViolation:
        db.commit() 
        return "User with email or username already exists", 400 
    except:
        db.commit() 
        return "Internal server error", 500

app.run("0.0.0.0", 8080, debug=True)



