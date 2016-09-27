# config file for my app
# make all the changes in case you want other configuration
import os


def get_environment_var(env_name, default_value):
    """
    Map the os.environment to return actual value or a default one.

    :param env_name: environment variable that is searched
    :param default_value: default value to be return
    :return: env_variable
    """
    if env_name in os.environ:
        return os.environ[env_name]
    else:
        return default_value

# global settings
JSON_PATH = "app/subreddits.json"
WAIT_TIME = int(get_environment_var('LONG_SCRIPT_WAIT', 300))

# mongo configuration
MONGO_SERVER = get_environment_var('MONGO_SERVER', "0.0.0.0")
MONGO_PORT = int(get_environment_var('MONGO_PORT', 27017))

DATABASE_NAME = get_environment_var('DATABASE_NAME', "hootsuite-challenge")

# flask configuration
WEB_SERVER = get_environment_var('WEB_SERVER', "0.0.0.0")
WEB_PORT = int(get_environment_var('WEB_PORT', 5000))
