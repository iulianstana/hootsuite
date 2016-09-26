import praw
import time
import json

import mongodb_wrapper


class RedditWrapper:

    def __init__(self, subreddit, time_period=None, db=None):
        """
        Initialize a new object that will manage subreddit submissions
        and comments. Fetch them from reddit.

        :param subreddit: subreddit name (string)
        :param time_period: time of last created new submissions/comments
                            (integer, time in seconds)
        :param db: add database for less database connections
        """
        self.reddit_obj = praw.Reddit(user_agent="Hootsuite challenge")

        if time_period:
            self.time_database = False
            self.time_period = time.time() - time_period
        else:
            self.time_database = True
            self.time_period = None
        self.subreddit = subreddit
        self.db = db

    def fetch_submissions(self):
        """
        Fetch all submissions in the last self.time_period window.

        :return a list of all new submissions
        """
        new_submissions = []
        try:
            submission_gen = self.reddit_obj.get_subreddit(self.subreddit)\
                                            .get_new(limit=None)

            for submission in submission_gen:
                if submission.created_utc < self.time_period:
                    break
                new_submissions.append({
                    'created': submission.created_utc,
                    'title': submission.title,
                    'type': 'submission',
                    'subreddit': self.subreddit
                })
        except praw.errors.InvalidSubreddit:
            print "Invalid Subreddit: no results"
        return new_submissions

    def fetch_comments(self):
        """
        Fetch all comments in the last self.time_period window.

        :return a list of all new comments
        """
        new_comments = []
        try:
            comments_gen = self.reddit_obj.get_comments(self.subreddit)

            for comment in comments_gen:
                if comment.created_utc < self.time_period:
                    break
                new_comments.append({
                    'created': comment.created_utc,
                    'comment': comment.body,
                    'type': 'comment',
                    'subreddit': self.subreddit
                })
        except praw.errors.InvalidSubreddit:
            print "Invalid Subreddit: no results"
        return new_comments

    def print_subreddit_data(self):
        """
        Get data for this subreddit. And print it to stdout.
        """
        print self.fetch_submissions()
        print self.fetch_comments()

    def save_subreddit_data(self):
        """
        Fetch data using this wrapper and save data in a database.
        In case no time_period is provide, use last update date saved in
        database.
        """
        if not self.db:
            self.db = mongodb_wrapper.connect_database()

        # get submissions and save them
        if self.time_database:
            # get last update time
            self.time_period = mongodb_wrapper.get_reddit_time(self.db,
                                                               self.subreddit,
                                                               "submission")
            # update with current time
            mongodb_wrapper.update_reddit_time(self.db,
                                               self.subreddit,
                                               submission_t=time.time())
        # get submissions
        items = self.fetch_submissions()
        # save in db
        mongodb_wrapper.insert_new_items(self.db, items)

        # get comments and save them
        if self.time_database:
            # get last update time
            self.time_period = mongodb_wrapper.get_reddit_time(self.db,
                                                               self.subreddit,
                                                               "comment")
            # update with current time
            mongodb_wrapper.update_reddit_time(self.db,
                                               self.subreddit,
                                               comment_t=time.time())
        # get comments
        items = self.fetch_comments()
        # save in db
        mongodb_wrapper.insert_new_items(self.db, items)


if __name__ == "__main__":
    with open('subreddits.json') as json_file:
        subreddits = json.load(json_file)
        for subreddit in subreddits['subreddits']:
            print "%s" % subreddit
            reddit = RedditWrapper(subreddit, 900)
            reddit.print_subreddit_data()
