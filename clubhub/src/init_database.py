from __future__ import annotations
from os import utime
import psycopg2
import pathlib
import util

def initialize_database(conn : psycopg2.connection, init_script : str):

    cur = conn.cursor()
    script_content = pathlib.Path(init_script).read_text()
    print(f"Init script: {script_content}")

    res = cur.execute(script_content)

    conn.commit()

    print("Response: ", res)
    


if __name__ == "__main__":
    config = util.load_configuration()
    db_url = config["DATABASE_URL"]
    db_conn = util.open_database(db_url)

    initialize_database(db_conn, "./queries/init.sql")
