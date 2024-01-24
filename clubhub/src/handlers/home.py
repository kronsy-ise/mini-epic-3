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

home_app = Blueprint('home_app', __name__)




@home_app.get("/home")
def homepage():
    auth_user = util.verify_session()

    if auth_user == None:
        return redirect("/")

    # Depending on the type of registered user 
    # we show a different home page
    
    if auth_user.is_admin:
        return render_template("admin/home.html")
    elif auth_user.kind == UserKind.User:
        return render_template("user/home.html")
    elif auth_user.kind == UserKind.Coordinator:
        return render_template("coordinator/home.html")
    else:
        return render_template("awaiting_approval.html")
