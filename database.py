from faunadb import query
from faunadb.client import FaunaClient
import os

fauna_key = os.environ['FAUNAKEY']
clientf = FaunaClient(fauna_key)

def get_all_cource():
    result = clientf.query(query.map_(query.lambda_("x", query.get(query.var('x'))),
                                      query.paginate(query.match(query.index('all_courses')))))
    result = result['data']
    data = [cource['data'] for cource in result]

    return data


def user_exists(user_id):
    res = clientf.query(query.map_(query.lambda_("x", query.get(query.var('x'))),
                                   query.paginate(query.match(query.index('users_by_id'), user_id))))
    return bool(len(res['data']))


def add_user(user_id, user_name):
    clientf.query(
        query.create(query.collection('Users'), {'data': {'user_id': user_id, 'user_name': user_name, 'active': 1}}))


def set_acive(user_id, acive):
    clientf.query(
        query.update(query.select('ref', query.get(query.match(query.index("users_by_id"), user_id))),
                     {'data': {'active': acive}}))


def get_users():
    res = clientf.query(query.map_(query.lambda_("x", query.get(query.var('x'))),
                                   query.paginate(query.match(query.index('get_all_users')))))

    data = [x['data'] for x in res['data']]

    for i in data:
        del i['user_name']

    return data
