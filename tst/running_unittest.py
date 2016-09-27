import unittest
import sys

import pymongo
import mock

from StringIO import StringIO
from contextlib import contextmanager

from run_webserver import get_items_from_database
from app import mongodb_wrapper


@contextmanager
def captured_output():
    """
    Function to capture stdout. Used to ignore print
    """
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


class TestRunning(unittest.TestCase):
    def setUp(self):
        mongodb_wrapper.connect_database = mock.Mock(return_value=None)

    @mock.patch('run_webserver.connect_database')
    def test_get_db_items_no_db_connection(self, connection):
        """ error when not db_connection """

        # mock methods
        connection.return_value = None

        # call function
        with captured_output() as (out, err):
            items = get_items_from_database('python', 0, 1000, None)

        # see results
        self.assertEqual(connection.call_count, 1)
        self.assertEqual(items, {'error': "AttributeError: 'NoneType' object has no attribute 'items'"})

    @mock.patch('run_webserver.connect_database')
    @mock.patch('pymongo.cursor.Cursor.hint')
    def test_get_db_items(self, find, connection):
        """ test if return value are in the correct form """

        # mock methods
        connection.return_value = pymongo.MongoClient()['test']
        find.return_value = [{"_id": 1,
                              "created": 1,
                              "subreddit": 'python',
                              "type": "comment",
                              "comment": "new"}]

        # call function
        items = get_items_from_database('python', 0, 1000, None)

        # see results
        self.assertEqual(connection.call_count, 1)
        # exclude subreddit and change '_id' to 'id'
        self.assertEqual(items, [{'comment': 'new',
                                  'created': 1,
                                  'id': '1',
                                  'type': 'comment'}])

    @mock.patch('run_webserver.connect_database')
    @mock.patch('pymongo.cursor.Cursor.hint')
    def test_get_db_items_no_items(self, find, connection):
        """ test when no items are returned """

        # mock methods
        connection.return_value = pymongo.MongoClient()['test']
        find.return_value = []

        # call function
        items = get_items_from_database('python', 0, 1000, None)

        # see results
        self.assertEqual(connection.call_count, 1)
        self.assertEqual(items, [])

if __name__ == '__main__':
    unittest.main()
