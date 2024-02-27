from __future__ import annotations
import psycopg2
from urllib.parse import urlparse
from flask import request


# my_path = os.path.abspath(os.path.dirname(__file__))
# CONFIG_PATH = os.path.join(my_path, "..", "config.json")



def open_database(database_url) -> psycopg2.connection:
    print("DATABASE URL: ", database_url)
    url = urlparse(url=database_url, scheme="postgres")

    db_username = url.username
    db_password = url.password
    db_path = url.path[1:]
    db_port = url.port
    db_host= url.hostname

    print("username", db_username)
    print("password", db_password)
    print("path", db_path)
    print("port", db_port)
    print("host", db_host)
    db = psycopg2.connect(user=db_username, password=db_password, database=db_path, port=db_port, host=db_host)

    return db




def verify_session():
    
    from globals import db
    from models.user import User

    session_secret = request.cookies.get("session")
    if session_secret is None:
        return None
    cur = db.cursor()

    try:
        cur.execute("SELECT user_id, expires_at FROM Sessions WHERE expires_at > NOW() AND secret = %s", (session_secret, ))
    except Exception as e:
        db.rollback()   
        raise e

    session = cur.fetchone()
    if session is None:
        return None

    user_id : int = session[0]

    user = User.fetch(user_id)

    return user
