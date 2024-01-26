from __future__ import annotations
from flask import Blueprint, redirect, render_template, request, url_for
from globals import db
from models.user import User
from models.user import UserKind
import bcrypt
import psycopg2.errors as pgerrors
from util import verify_session


users_app = Blueprint('users_app', __name__)

@users_app.post("/api/users/<id>/approve")
def approve_user(id):


    auth_user = verify_session()

    if auth_user is None:
        return "Unauthorized to perform action", 403 
    elif not auth_user.UserKind.Admin:
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

@users_app.get("/api/users")
def get_all_users():
    user = verify_session()

    if user is None:
        return "Authorization is required to view all users", 403
    elif user.kind == UserKind.User:
        return "Normal users may only view their own profile", 403
    elif user.kind == UserKind.Coordinator and not user.is_admin:
        return "You may only view members of your clubs, please check users via GET /api/clubs/<id>/members", 403

    cur = db.cursor()
    cur.execute("""
    SELECT username, email, mobile, user_kind, id FROM Users
    """)
    users = cur.fetchall()

    response = []

    for user in users:
        username = user[0]
        email = user[1]
        mobile = user[2]
        kind = user[3]
        id = user[4]

        response.append({
            "username" : username,
            "email" : email,
            "mobile" : mobile,
            "kind" : kind,
            "id" : id
        })

    print(response)
    return response


@users_app.post("/api/users")
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
    kind = "admin" if is_admin else "unapproved"

    print(f"User count: {user_count}")

    try:
    # Create the user
        cur.execute("""
    INSERT INTO Users(username, name, email, mobile, password_hash, user_kind)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (username, name, email, mobile, password_hash.decode("utf-8"), kind))
   
        db.commit()

        return "Successfully created user, waiting admin approval", 201
    
    except pgerrors.UniqueViolation:
        db.commit() 
        return "User with email or username already exists", 400 
    except:
        db.commit() 
        return "Internal server error", 500


@users_app.route("/api/users")
#returns a list of all users
def get_users():
    users = User.query.all()
    return render_template('users.html', users=users)
@users_app.route("/api/users/<id>/delete", methods=['POST'])
def delete_user(id):
    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('get_users'))

# @users_app.patch("/api/users/<user_id>")
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
