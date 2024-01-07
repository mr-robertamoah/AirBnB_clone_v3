!/usr/bin/python3
"""" Initializes Flask Blueprint """

from api.v1.views.amenities import *
from api.v1.views.cities import *
from api.v1.views.index import *
from api.v1.views.places_amenities import *
from api.v1.views.places import *
from api.v1.views.places_reviews import *
from api.v1.views.states import *
from api.v1.views.users import *
from flask import Blueprint, request
from werkzeug.exceptions import MethodNotAllowed


app_views = Blueprint('app_views', __name__, url_prefix='/api/v1')

def get_entity(entities, id):
    ''' get an entity if id is given or raise NotFound '''

    if id is None:
        return None

    _list = list(filter(lambda x: x.id == id, entities))
    if _list is None or len(_list) < 1:
        raise NotFound()

    return _list[0]

def call_route_method(**kwargs):
    ''' call the appropriate method related to a route and method '''

    handlers = {
        'GET': _get,
        'DELETE': _delete,
        'POST': _post,
        'PUT': _put,
    }

    if request.method in handlers:
        return handlers[request.method](**kwargs)

    raise MethodNotAllowed(list(handlers.keys()))
