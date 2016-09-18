import json
import time

from app.mongodb_wrapper import connect_database, reset_reddit_time
from app.reddit_wrapper import RedditWrapper


def read_json_file(path):
    """
    Read json file from a specific path and return the subreddits

    :param path: path of json file that contains subreddits to be read
    :return: list of subreddits
    """
    subreddits = []
    try:
        with open(path) as json_file:
            subreddits = json.load(json_file)['subreddits']
    except IOError as exp:
        print exp
    return subreddits


def reset_subreddit_times(db, subreddits):
    """
    Need to restart subreddits time in order to get just the generate
    data from running script interval

    :param db: mongo database object
    :param subreddits: list of subreddits that will reset their times
    """
    for subreddit in subreddits:
        reset_reddit_time(db, subreddit)


def run_reader(db, subreddits):
    """
    Start fetching data and save it in database

    :param db: mongo database object
    :param subreddits: list of subreddits that will be monitoring
    :return:
    """
    if subreddits_list:
        while True:
            # times are restarted, start with a wait
            time.sleep(300)

            for subreddit in subreddits:
                print "%s" % subreddit
                reddit = RedditWrapper(subreddit, db=db)
                reddit.save_subreddit_data()
    else:
        print "no reddits to fetch"


if __name__ == "__main__":
    subreddits_list = read_json_file("app/subreddits.json")

    # connect to database and reset the last update times
    db_connection = connect_database("localhost", 27017)
    reset_subreddit_times(db_connection, subreddits_list)

    # start periodically fetching
    run_reader(db_connection, subreddits_list)
