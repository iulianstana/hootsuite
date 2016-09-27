import unittest
import mock
import sys
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
        """ error when not db_connection
        """
        connection.return_value = None
        # mock methods
        with captured_output() as (out, err):
            items = get_items_from_database('python', 0, 1000, None)

        # see results
        self.assertEqual(connection.call_count, 1)
        self.assertEqual(items, {'error': "AttributeError: 'NoneType' object has no attribute 'items'"})


if __name__ == '__main__':
    unittest.main()
