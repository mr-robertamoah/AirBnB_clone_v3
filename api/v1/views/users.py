#!/usr/bin/python3
'''
contains implementation of the following routes:
    /users
    /users/<user_id>
'''

from api.v1.views import app_views, call_route_method,\
validate_data, remove_keys, get_entity
from flask import jsonify, request
from models import storage
from models.user import User
from werkzeug.exceptions import NotFound, BadRequest


ROUTE_METHODS = ['GET', 'DELETE', 'POST', 'PUT']


@app_views.route('/users', methods=ROUTE_METHODS)
@app_views.route('/users/<user_id>', methods=ROUTE_METHODS)
def handle_users(user_id=None):
    ''' handles routes relating to users '''
    handlers = {
        'GET': get_users,
        'DELETE': delete_user,
        'POST': post_user,
        'PUT': put_user,
    }

    return call_route_method(handlers, **{"user_id": user_id})


def get_users(user_id=None):
    ''' get users or user with user_id '''
    all_users = storage.all(User).values()
    user = get_entity(all_users, user_id)
    if user:
        obj = remove_keys(user.to_dict(), ["places", "reviews"])
        return jsonify(obj)

    users = []
    for u in all_users:
        obj = remove_keys(u.to_dict(), ["places", "reviews"])
        users.append(obj)
    return jsonify(users)


def delete_user(user_id=None):
    ''' delete user with user_id '''
    user = storage.get(User, user_id)
    if user is None:
        raise NotFound()

    storage.delete(user)
    storage.save()
    return jsonify({}), 200


def post_user(user_id=None):
    ''' add new user to storage '''
    data = request.get_json()
    validate_data(data, ["email", "password"])
    user = User(**data)
    user.save()
    obj = remove_keys(user.to_dict(), ["places", "reviews"])
    return jsonify(obj), 201


def put_user(user_id=None):
    ''' updates user with user_id '''
    xkeys = ('id', 'email', 'created_at', 'updated_at')
    user = storage.get(User, user_id)
    if user is None:
        raise NotFound()

    data = request.get_json()
    validate_data(data, includeKey=False)
    for key, value in data.items():
        if key not in xkeys:
            setattr(user, key, value)
    user.save()
    obj = remove_keys(user.to_dict(), ["places", "reviews"])
    return jsonify(obj), 200
