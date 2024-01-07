#!/usr/bin/python3
"""" Initializes Flask Blueprint """

from flask import Blueprint, request
from werkzeug.exceptions import MethodNotAllowed, NotFound, BadRequest


app_views = Blueprint('app_views', __name__, url_prefix='/api/v1')


def remove_keys(_dict, keys):
    ''' remove keys for dictionary if they exist '''
    for key in keys:
        if key in _dict.keys():
            del _dict[key]

    return _dict


def validate_data(data, key="name", includeKey=True):
    ''' ensures json_data is valid '''
    if type(data) is not dict:
        raise BadRequest(description='Not a JSON')

    if type(key) is str and key not in data and includeKey:
        raise BadRequest(description="Missing {}".format(key))

    if type(key) is list and len(key) and includeKey:
        for k in key:
            if k not in data:
                raise BadRequest(description="Missing {}".format(k))


def get_entity(entities, id, raiseException=False):
    ''' get an entity if id is given or raise NotFound '''

    if id is None:
        if raiseException:
            raise NotFound()
        return None

    _list = list(filter(lambda x: x.id == id, entities))
    if _list is None or len(_list) < 1:
        raise NotFound()

    return _list[0]


def call_route_method(handlers, **kwargs):
    ''' call the appropriate method related to a route and method '''
    if request.method in handlers:
        return handlers[request.method](**kwargs)

    raise MethodNotAllowed(list(handlers.keys()))


from api.v1.views.amenities import *
from api.v1.views.cities import *
from api.v1.views.index import *
from api.v1.views.places_amenities import *
from api.v1.views.places import *
from api.v1.views.places_reviews import *
from api.v1.views.states import *
from api.v1.views.users import *
