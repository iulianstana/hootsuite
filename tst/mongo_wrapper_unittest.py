import unittest
import mock
from app.mongodb_wrapper import connect_database, \
    insert_new_items, insert_new_setting


class TestMongoWrapper(unittest.TestCase):

    @mock.patch('pymongo.MongoClient.__init__')
    @mock.patch('pymongo.MongoClient.__getitem__')
    def test_connect_database(self, mongoclient, mongo_init):
        """ see if MongoClient is called and is returning things
        """

        # mock methods
        mongoclient.return_value = False
        mongo_init.return_value = None
        db = connect_database(database_name='my_db')

        # see results
        self.assertEqual(db, False)
        self.assertEqual(mongo_init.call_args_list[0][0], ('localhost', 27017))
        self.assertEqual(mongoclient.call_count, 1)

    @mock.patch('pymongo.collection.Collection.insert_many')
    def test_insert_new_items(self, insert_many):
        """
        test to see if insert_many works well
        """
        db = connect_database()

        # call function
        result = insert_new_items(db, {'a': 1, 'b': 2})

        # see results
        self.assertEqual(result, True)
        self.assertEqual(insert_many.call_args_list[0][0][0], {'a': 1, 'b': 2})

    @mock.patch('pymongo.collection.Collection.insert_one')
    def test_insert_new_setting(self, insert_one):
        """
        test to see if insert_many works well
        """
        db = connect_database()

        # call function
        result = insert_new_setting(db, 'python', 1000, 2000)

        # see results
        self.assertEqual(type(result), dict)
        argument = insert_one.call_args_list[0][0][0]
        # insert_one argument values
        self.assertEqual(argument['subreddit'], 'python')
        self.assertEqual(argument['times']['submission'], 1000)
        self.assertEqual(argument['times']['comment'], 2000)
        # result values
        self.assertEqual(result['subreddit'], 'python')
        self.assertEqual(result['times']['submission'], 1000)
        self.assertEqual(result['times']['comment'], 2000)


if __name__ == '__main__':
    unittest.main()
