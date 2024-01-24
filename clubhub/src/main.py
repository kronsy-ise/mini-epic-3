from __future__ import annotations
from typing import Optional
from flask import Flask, request, request_finished, session, make_response, redirect, render_template
import psycopg2
from psycopg2 import errors as pgerrors
import random
import bcrypt
import datetime
from handlers.users import users_app
from handlers.auth import auth_app
from handlers.home import home_app

from util import verify_session
from globals import db

from models.user import User, UserKind

app = Flask(__name__)

app.register_blueprint(users_app)
app.register_blueprint(auth_app)
app.register_blueprint(home_app)


@app.get("/")
def home():
    """
    When a user hits the home page,
    we check their auth status 

    if they are logged in,
    we redirect them to the appropriate page 

    otherwise we redirect them to the login form
    """

    auth_user = verify_session()


    if auth_user == None:
        # Redirect to login 
        return redirect("/login")
    else:
        return redirect("/home")



app.run("0.0.0.0", 8080, debug=True)

