import util
import os
db_url = os.environ["DATABASE_URL"]

db = util.open_database(db_url)
