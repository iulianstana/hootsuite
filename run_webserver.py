from flask import Flask, jsonify
from flask import request
from flask import abort
from flask import make_response

from app.mongodb_wrapper import connect_database
from config import MONGO_SERVER, \
                   MONGO_PORT, \
                   DATABASE_NAME, \
                   WEB_SERVER, \
                   WEB_PORT


app = Flask(__name__)


@app.errorhandler(404)
def not_found(error):
    """ Handler 404 error in a better way """
    return make_response(jsonify({'error': 'Not found'}), 404)


def make_public_item(item):
    """
    Convert the current item into the delivered one.

    :param item: database item (dictionary)
    :return: item that will be public (dictionary)
    """
    new_task = {}
    for field in item:
        if field == 'subreddit':
            continue
        if field == '_id':
            new_task['id'] = str(item['_id'])
        else:
            new_task[field] = item[field]
    return new_task


def get_items_from_database(subreddit, start_time, end_time, keyword):
    """
    Get items from database, manipulate them and pass them
    further.
    Keyword parameter can be used to add an additional search
    level to search in comments or title after a specific keyword

    :param subreddit: subreddit name used for search (string)
    :param start_time: item created start time (integer)
    :param end_time: item created end time (integer)
    :param keyword: used to search after a specific key (string)
    :return: list of items
    """
    # get a database connection
    db = connect_database(server=MONGO_SERVER,
                          port=MONGO_PORT,
                          database_name=DATABASE_NAME)
    items = []
    search_field = {"subreddit": subreddit,
                    "created": {"$gte": start_time,
                                "$lte": end_time}
                    }
    if keyword:
        search_field["$or"] = [{"title": {"$regex": keyword, '$options': 'i'}},
                               {"comment": {"$regex": keyword, '$options': 'i'}}]
    try:
        for item in db.items.find(search_field)\
                            .hint('subreddit_1_created_-1'):
            items.append(make_public_item(item))

    except AttributeError as exp:
        items = {'error': 'AttributeError: %s' % exp}
        print exp

    return items


@app.route('/items/', methods=['GET'])
def get_items():
    """
    Use GET method to get items for a specific subreddit provided by request.
    Use window time frame to get items.
    """
    subreddit = request.args.get('subreddit')
    start_time = request.args.get('from')
    end_time = request.args.get('to')
    keyword = request.args.get('keyword')

    if subreddit is None or start_time is None or end_time is None:
        abort(400)
    try:
        start_time = int(start_time)
        end_time = int(end_time)
    except ValueError as _:
        abort(400)

    items = get_items_from_database(subreddit, start_time, end_time, keyword)

    return jsonify(items)


if __name__ == '__main__':
    print "Start flask server"
    app.run(host=WEB_SERVER, port=WEB_PORT, debug=True)
