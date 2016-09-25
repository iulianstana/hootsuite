# config file for my app
# make all the changes in case you want other configuration
import os

# global settings
JSON_PATH = "app/subreddits.json"
WAIT_TIME = 300

# mongo configuration
MONGO_SERVER = os.environ['MONGO_SERVER'] if 'MONGO_SERVER' in os.environ else "0.0.0.0"
MONGO_PORT = int(os.environ['MONGO_PORT']) if 'MONGO_PORT' in os.environ else 27017

DATABASE_NAME = os.environ['DATABASE_NAME'] if 'DATABASE_NAME' in os.environ else "hootsuite-challenge"

# flask configuration
WEB_SERVER = os.environ['WEB_SERVER'] if 'WEB_SERVER' in os.environ else "0.0.0.0"
WEB_PORT = int(os.environ['WEB_PORT']) if 'WEB_PORT' in os.environ else 5000