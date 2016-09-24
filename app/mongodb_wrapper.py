from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import time

DATABASE_NAME = 'hootsuite-challenge'


def connect_database(server='localhost', port=27017, database_name=DATABASE_NAME):
    """
    Connect to mongo database.

    :param server: mongo server host name (string)
    :param port: listening port of mongo server (integer)
    :param database_name: name of the database in use (string)
    :return: database object
    """
    result = None
    try:
        client = MongoClient(server, port)
        result = client[database_name]

        # test server is up.
        client.server_info()
    except ServerSelectionTimeoutError as exp:
        result = None
        print "No connection %s" % exp
    return result


def insert_new_setting(db, subreddit, submission_t=None, comment_t=None):
    """
    Create a new reddit setting with given time value for submission and
    comment. Use current time in case no value is given.

    :param db: mongo database object
    :param subreddit: new reddit name (string)
    :param submission_t: set submission time to a specific value (integer)
    :param comment_t: set comment time to a specific value (integer)
    :return: reddit setting
    """
    reddit_setting = {}
    try:
        reddit_setting = {
            'subreddit': subreddit,
            'times': {
                'submission': submission_t if submission_t else time.time(),
                'comment': comment_t if comment_t else time.time()
            }
        }
        db.dynamic_settings.insert_one(reddit_setting)
    except AttributeError as exp:
        print exp
    return reddit_setting


def update_reddit_time(db, subreddit, submission_t=None, comment_t=None):
    """
    Update a reddit setting time with new values.

    :param db: mongo database object
    :param subreddit: reddit name of whose setting will be update (string)
    :param submission_t: set submission time to a specific value (integer)
    :param comment_t: set comment time to a specific value (integer)
    :return:
    """
    try:
        reddit_setting = db.dynamic_settings.find_one({'subreddit': subreddit})
        if submission_t:
            reddit_setting['times']['submission'] = submission_t
        if comment_t:
            reddit_setting['times']['comment'] = comment_t
        db.dynamic_settings.replace_one({'subreddit': subreddit}, reddit_setting)
    except Exception as _:
        # probably given subreddit doesn't exist in our database
        # create new dynamic setting for this new subreddit
        insert_new_setting(db, subreddit, submission_t, comment_t)


def reset_reddit_time(db, subreddit):
    """
    Reset setting times to the current values.

    :param db: mongo database object
    :param subreddit: reddit name of whose setting will be reset (string)
    """
    update_reddit_time(db,
                       subreddit,
                       submission_t=time.time(),
                       comment_t=time.time())


def get_reddit_time(db, subreddit, time_type):
    """
    Get settled time of "comment" or "submission of a given subreddit.

    :param db: mongo database object
    :param subreddit: reddit name of whose setting will be reset (string)
    :param time_type: "comment"|"submission"
    """
    reddit_setting = db.dynamic_settings.find_one({'subreddit': subreddit})
    if not reddit_setting:
        reddit_setting = insert_new_setting(db, subreddit)
    return reddit_setting['times'][time_type]


def insert_new_items(db, new_items):
    """
    Insert new items in database for a specific subreddit
    :param db: mongo database object
    :param new_items: list of new items to be inserted (list)
    :return: boolean value (True the insert was done | False otherwise)
    """
    result = False
    try:
        if new_items:
            db.items.insert_many(new_items)
            result = True
    except AttributeError as exp:
        print exp
    return result


if __name__ == "__main__":
    db_connection = connect_database()
    update_reddit_time(db_connection, 'python', 3000, 3000)

    print "last comment update: %s" % get_reddit_time(db_connection,
                                                      'python',
                                                      'comment')
    reset_reddit_time(db_connection, 'python')
    print "reset comment update: %s" % get_reddit_time(db_connection,
                                                       'python',
                                                       'comment')
