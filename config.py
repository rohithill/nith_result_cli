# Name of the folder to store result
RESULT_DIR = 'result-async-tempo'

# Name of the database to create from RESULT_DIR folder
DB_NAME = 'result.db'

# Limit on number of concurrent downloads
# Large number (>1000) may give errors on select.
# Preferably 100
CONCURRENCY_LIMIT = 50