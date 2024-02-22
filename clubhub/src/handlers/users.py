from __future__ import annotations
from flask import Blueprint, redirect, render_template, request, url_for
from globals import db
from models.user import User
from models.user import UserKind
import bcrypt
import psycopg2.errors as pgerrors
from util import verify_session


users_app = Blueprint('users_app', __name__)

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
    response = redirect("/home")

    # Close the cursor and connection
    return response

@users_app.route('/reject-user/<int:user_id>', methods=['POST'])
def reject(user_id):
    # Connect to your database
    
    cur = db.cursor()

    # Create a cursor
    # Execute the UPDATE statement
    cur.execute("DELETE FROM USERS WHERE user_id = %s", (user_id,))

    # Commit the changes
    db.commit()
    response = redirect("/home")

    # Close the cursor and connection
    return response
