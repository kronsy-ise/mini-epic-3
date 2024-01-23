from __future__ import annotations

import json
import psycopg2
from urllib.parse import urlparse
import pathlib
import os


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
