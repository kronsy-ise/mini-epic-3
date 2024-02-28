from __future__ import annotations
import psycopg2
import pathlib
import util
import os

def maybe_initialize_database(conn : psycopg2.connection, init_script : str):
    """
    Initialize the database if it is not already initialized 
    """
    cur = conn.cursor()

    # Check for initialization by looking for users table
    cur.execute("SELECT EXISTS(SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = 'users')")
    res : tuple[bool] = cur.fetchone()
    print(res)
    if res[0] == False:
        # Database isnt initialized, initialize it
        print("Initializing Database!")
        initialize_database(conn, init_script)

def initialize_database(conn : psycopg2.connection, init_script : str):

    cur = conn.cursor()
    script_content = pathlib.Path(init_script).read_text()

    res = cur.execute(script_content)

    conn.commit()

    print("Response: ", res)

INIT_SCRIPT = os.path.join(util.my_path, "..", "queries", "init.sql")


if __name__ == "__main__":
    import globals
    initialize_database(globals.db, INIT_SCRIPT)
