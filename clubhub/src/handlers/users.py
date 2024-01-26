from __future__ import annotations
from flask import Blueprint, redirect, render_template, request, url_for
from globals import db
from models.user import User
from models.user import UserKind
import bcrypt
import psycopg2.errors as pgerrors
from util import verify_session


users_app = Blueprint('users_app', __name__)