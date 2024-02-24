import util

config = util.load_configuration()
print(f'DATABASE_URL: {config["DATABASE_URL"]}')  # debug print statement
db = util.open_database(config["DATABASE_URL"])
