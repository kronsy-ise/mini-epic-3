import util

config = util.load_configuration()
db = util.open_database(config["DATABASE_URL"])
