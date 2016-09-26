import unittest
import mock
import time
from app.reddit_wrapper import RedditWrapper


class TestRedditWrapper(unittest.TestCase):
    def setUp(self):
        self.time_frame = 900

    def mock_new_submissions(self):
        """
        Mock function that returns a stable list of values
        for submissions
        """
        class Submission:
            def __init__(self, created_time, title):
                self.created_utc = created_time
                self.title = title

        submissions = [
            Submission(time.time() - self.time_frame + 200, "a"),
            Submission(time.time() - self.time_frame + 100, "b"),
            Submission(time.time() - self.time_frame - 100, "c"),
            Submission(time.time() - self.time_frame - 200, "d")
        ]
        return submissions

    def mock_new_comments(self):
        """
        Mock function that returns a stable list of values
        for comments
        """
        class Comments:
            def __init__(self, created_time, title):
                self.created_utc = created_time
                self.body = title

        submissions = [
            Comments(time.time() - self.time_frame + 250, "a"),
            Comments(time.time() - self.time_frame + 200, "b"),
            Comments(time.time() - self.time_frame + 100, "c"),
            Comments(time.time() - self.time_frame - 100, "d"),
            Comments(time.time() - self.time_frame - 200, "e")
        ]
        return submissions

    def test_object_fields_set(self):
        """ test if object fields are set """
        reddit_obj = RedditWrapper('python', self.time_frame)
        # see if the subreddit was seated correct
        self.assertEqual(reddit_obj.subreddit, 'python')

        # test to see if time_database and time_period
        # are seated correct
        self.assertFalse(reddit_obj.time_database)
        self.assertTrue(reddit_obj.time_period)

        # database was not provided
        self.assertEqual(reddit_obj.db, None)

    @mock.patch('praw.objects.Subreddit.get_new')
    def test_fetch_submission(self, get_new):
        """ mock up get_new submission function and test
        RedditWrapper.fetch_submissions
        """

        # initialize reddit_obj
        reddit_obj = RedditWrapper('python', self.time_frame)
        get_new.return_value = self.mock_new_submissions()

        submissions = reddit_obj.fetch_submissions()
        self.assertEqual(submissions[0]['title'], 'a')
        self.assertEqual(submissions[0]['subreddit'], 'python')
        self.assertEqual(submissions[0]['type'], 'submission')
        self.assertEqual(len(submissions), 2)

    @mock.patch('praw.objects.Subreddit.get_new')
    def test_fetch_submission_nothing_new(self, get_new):
        """ mock up get_new submission function and test
        RedditWrapper.fetch_submissions
        No new submissions
        """

        # initialize reddit_obj
        reddit_obj = RedditWrapper('python', self.time_frame - 300)
        get_new.return_value = self.mock_new_submissions()

        submissions = reddit_obj.fetch_submissions()
        self.assertEqual(len(submissions), 0)

    @mock.patch('praw.Reddit.get_comments')
    def test_fetch_comments(self, get_comments):
        """ mock up get_comments function and test
        RedditWrapper.fet_comments
        """

        # initialize reddit_obj
        reddit_obj = RedditWrapper('python', self.time_frame)

        # mock Reddit.get_comments method
        get_comments.return_value = self.mock_new_comments()

        # test my function
        comments = reddit_obj.fetch_comments()

        # see results
        self.assertEqual(comments[0]['comment'], 'a')
        self.assertEqual(comments[0]['subreddit'], 'python')
        self.assertEqual(comments[0]['type'], 'comment')
        self.assertEqual(len(comments), 3)

    @mock.patch('praw.Reddit.get_comments')
    def test_fetch_comments_nothing_new(self, get_comments):
        """ mock up get_comments function and test
        RedditWrapper.fet_comments
        No new comments.
        """

        # initialize reddit_obj
        reddit_obj = RedditWrapper('python', self.time_frame - 300)

        # mock Reddit.get_comments method
        get_comments.return_value = self.mock_new_comments()

        # test my function
        comments = reddit_obj.fetch_comments()

        # see results
        self.assertEqual(len(comments), 0)

    @mock.patch('app.mongodb_wrapper.connect_database')
    @mock.patch('app.mongodb_wrapper.get_reddit_time')
    @mock.patch('praw.objects.Subreddit.get_new')
    @mock.patch('praw.Reddit.get_comments')
    @mock.patch('app.mongodb_wrapper.insert_new_items')
    def test_save_reddit_data(self, insert_items, get_comments, get_new,
                              get_reddit_time, connection):
        """
        Test to see if insert_new_items function is called correct
        """
        # initialize reddit_obj
        reddit_obj = RedditWrapper('python', self.time_frame)

        # mock methods
        get_new.return_value = self.mock_new_submissions()
        get_comments.return_value = self.mock_new_comments()

        # test my function
        reddit_obj.save_subreddit_data()

        # see results
        self.assertEqual(get_new.call_count, 1)
        self.assertEqual(get_comments.call_count, 1)
        self.assertEqual(get_reddit_time.call_count, 0)
        # two insertion had been made
        self.assertEqual(insert_items.call_count, 2)

        # get insert_new_items argument to see if the correct
        # number of items where send to the function
        submission_items = insert_items.call_args_list[0][0][1]
        self.assertEqual(len(submission_items), 2)

        comment_items = insert_items.call_args_list[1][0][1]
        self.assertEqual(len(comment_items), 3)

    @mock.patch('app.mongodb_wrapper.connect_database')
    @mock.patch('app.mongodb_wrapper.update_reddit_time')
    @mock.patch('app.mongodb_wrapper.get_reddit_time')
    @mock.patch('praw.objects.Subreddit.get_new')
    @mock.patch('praw.Reddit.get_comments')
    @mock.patch('app.mongodb_wrapper.insert_new_items')
    def test_save_reddit_data_reddit_time(self, insert_items, get_comments,
                                          get_new, get_reddit_t, update_t,
                                          connection):
        """
        Test to see if insert_new_items function is called correct
        and also time_database works correct
        """
        # initialize reddit_obj
        reddit_obj = RedditWrapper('python')

        # mock methods
        get_reddit_t.return_value = time.time() - self.time_frame
        get_new.return_value = self.mock_new_submissions()
        get_comments.return_value = self.mock_new_comments()

        # test my function
        reddit_obj.save_subreddit_data()

        # see results
        self.assertEqual(get_new.call_count, 1)
        self.assertEqual(get_comments.call_count, 1)
        self.assertEqual(get_reddit_t.call_count, 2)
        self.assertEqual(update_t.call_count, 2)
        # two insertion had been made
        self.assertEqual(insert_items.call_count, 2)

        # get insert_new_items argument to see if the correct
        # number of items where send to the function
        submission_items = insert_items.call_args_list[0][0][1]
        self.assertEqual(len(submission_items), 2)

        comment_items = insert_items.call_args_list[1][0][1]
        self.assertEqual(len(comment_items), 3)

if __name__ == '__main__':
    unittest.main()
