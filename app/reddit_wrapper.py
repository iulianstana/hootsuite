import praw
import time


class RedditWrapper:

    def __init__(self, subreddit, time_period):
        """
        Initialize a new object that will manage subreddit submissions
        and comments. Fetch them from reddit and print them to stdout.

        :param subreddit: subreddit name (string)
        :param time_period: time of last created new submissions/comments
                            (integer, time in seconds)
        """
        self.reddit_obj = praw.Reddit(user_agent="Hootsuite challenge")
        self.time_period = time.time() - time_period
        self.subreddit = subreddit

    def fetch_submissions(self):
        """
        Fetch all submissions in the last self.time_period window.

        :return a list of all new submissions
        """
        new_submissions = []
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

        return new_submissions

    def fetch_comments(self):
        """
        Fetch all comments in the last self.time_period window.

        :return a list of all new comments
        """
        new_comments = []
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
        return new_comments

    def save_subreddit_data(self):
        """
        Get data for this subreddit. And print it to stdout.
        """

        print self.fetch_submissions()
        print self.fetch_comments()


if __name__ == "__main__":
    reddit = RedditWrapper('python', 900)
    reddit.save_subreddit_data()
    reddit = RedditWrapper('OnePiece', 900)
    reddit.save_subreddit_data()