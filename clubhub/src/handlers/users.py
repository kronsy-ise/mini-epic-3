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