from flask import Flask, request
import psycopg2
from psycopg2 import errors as pgerrors
import util
import bcrypt

config = util.load_configuration()
db = util.open_database(config["DATABASE_URL"])


app = Flask(__name__)


@app.get("/api/users")
def get_all_users():
    # TODO: Add auth
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

    data = request.json

    if data is None:
        return "Expected Body", 400

    username : str = data["username"]
    password : str = data["password"]

    print("AA")
    cur = db.cursor()

    cur.execute("SELECT password FROM Users WHERE username = %s", (username))

    credential = cur.fetchone()

    if credential is None:
        return "User with username Not Found", 404

    password_hash : str = credential[0]

    password_hash_enc = password_hash.encode("utf-8")
    password_enc = password.encode("utf-8")

    is_valid_pw = bcrypt.checkpw(password_enc, password_hash_enc)

    if not is_valid_pw:
        return "Mismatched password", 403

    
    return "hello, world", 200


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
        """, (username, name, email, mobile, password_hash, is_admin, kind))
   
        db.commit()

        return "Successfully created user, waiting admin approval", 201
    
    except pgerrors.UniqueViolation:
        db.commit() 
        return "User with email or username already exists", 400 
    except:
        db.commit() 
        return "Internal server error", 500

app.run("0.0.0.0", 8080, debug=True)



