from __future__ import annotations
from flask import Blueprint, redirect, render_template,flash
from globals import db
from models.user import User
from models.user import UserKind
import psycopg2.errors as pgerrors
import util 


users_app = Blueprint('users_app', __name__)
@users_app.route('/users')
def users():
    auth_user = util.verify_session()

    if auth_user == None:
        return redirect("/")

    # Depending on the type of registered user 
    # we show a different home page
    
    if auth_user.kind == UserKind.Admin:
        users=User.return_list()
        num_lists = len(User.return_list())
        coord_count = 0
        student_count = 0
        for user in users:
            if user[3] == 'coordinator':
                coord_count += 1
            elif user[3] == 'student':
                student_count +=1
                
        return render_template("admin/users.html",users=users ,user_count=num_lists,
                               coord_count=coord_count,student_count=student_count,unapproved_count =num_lists-coord_count-student_count-1)
    elif auth_user.kind == UserKind.Student:
        return render_template("user/users.html")
    elif auth_user.kind == UserKind.Coordinator:
        return render_template("coordinator/users.html")
    else:
        return render_template("awaiting_approval.html")


@users_app.route('/approve-student/<int:student_id>', methods=['POST'])
def approve_student(student_id):
    # Connect to your database
    
    cur = db.cursor()

    # Create a cursor
    # Execute the UPDATE statement
    cur.execute("UPDATE USERS SET user_kind = 'student' WHERE user_id = %s", (student_id,))

    # Commit the changes
    db.commit()
    response = redirect("/home")

    # Close the cursor and connection
    cur.execute("UPDATE USERS SET user_kind = 'student' WHERE user_id = %s", (student_id,))
    return response

@users_app.route('/approve-coord/<int:coord_id>', methods=['POST'])
def approve_coordinator(coord_id):
    # Connect to your database
    
    cur = db.cursor()

    # Create a cursor
    # Execute the UPDATE statement
    cur.execute("UPDATE USERS SET user_kind = 'coordinator' WHERE user_id = %s", (coord_id,))

    # Commit the changes
    db.commit()
    response = redirect("/users")

    # Close the cursor and connection
    return response

@users_app.route('/reject-user/<int:user_id>', methods=['POST'])
def reject(user_id):
    # Connect to your database
    cur = db.cursor()
    # Execute the DELETE statement
    try:
        cur.execute("DELETE FROM USERS WHERE user_id = %s", (user_id,))
        db.commit()
    except pgerrors.ForeignKeyViolation as e:
        db.rollback()  # rollback the transaction
        flash("Cannot delete user because they are still referenced in the clubs table.")
    except Exception as e:
        db.rollback()  # rollback the transaction
        flash(e)
        
    response = redirect("/users")
    # Close the cursor and connection
    return response

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

