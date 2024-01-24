from __future__ import annotations

import json
import psycopg2
from urllib.parse import urlparse
import os
from flask import request


my_path = os.path.abspath(os.path.dirname(__file__))
CONFIG_PATH = os.path.join(my_path, "..", "config.json")

def load_configuration():
    config_file = open(CONFIG_PATH, "r")

    configuration = json.load(config_file)

    return configuration


def open_database(database_url) -> psycopg2.connection:
    url = urlparse(database_url)

    db_username = url.username
    db_password = url.password
    db_path = url.path[1:]
    db_port = url.port
    db_host= url.hostname

    db = psycopg2.connect(user=db_username, password=db_password, database=db_path, port=db_port, host=db_host)

    return db




def verify_session():
    
    from globals import db
    from models.user import User

    session_secret = request.cookies.get("session")
    if session_secret is None:
        return None
    cur = db.cursor()

    cur.execute("SELECT user_id, expires_at FROM Sessions WHERE expires_at > NOW() AND secret = %s", (session_secret, ))

    session = cur.fetchone()

    user_id : int = session[0]

    user = User.fetch(user_id)

    return user
