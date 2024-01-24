from __future__ import annotations
import psycopg2
import pathlib
import util
import os

def initialize_database(conn : psycopg2.connection, init_script : str):

    cur = conn.cursor()
    script_content = pathlib.Path(init_script).read_text()

    res = cur.execute(script_content)

    conn.commit()

    print("Response: ", res)
    


if __name__ == "__main__":
    config = util.load_configuration()
    db_url = config["DATABASE_URL"]
    db_conn = util.open_database(db_url)

    file = os.path.join(util.my_path, "..", "queries", "init.sql")
    
    initialize_database(db_conn, file)
