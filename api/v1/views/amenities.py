#!/usr/bin/python3
'''
Contains the amenities routes:
    /amenities
    /amenities/<amenity_id>
'''

from api.v1.views import app_views, get_entity, call_route_method
from flask import jsonify, request
from models import storage
from models.amenity import Amenity
from werkzeug.exceptions import NotFound, MethodNotAllowed, BadRequest


ROUTE_METHODS = ['GET', 'DELETE', 'POST', 'PUT']


@app_views.route('/amenities', methods=ROUTE_METHODS)
@app_views.route('/amenities/<amenity_id>', methods=ROUTE_METHODS)
def handle_amenities(amenity_id=None):
    ''' handles all routes regarding amenities '''

    args = {"amenity_id": amenity_id}
    call_route_method(**args)


def _get(amenity_id=None):
    ''' gets amenity with the given amenity_id or all amenities '''
    all_amenities = storage.all(Amenity).values()
    amenity = get_entity(all_amenities, amenity_id)
    if amenity:
        return jsonify(amenity.to_dict())

    all_amenities = list(map(lambda x: x.to_dict(), all_amenities))
    return jsonify(all_amenities)


def _delete(amenity_id=None):
    ''' deletes amenity with given amenity_id '''
    all_amenities = storage.all(Amenity).values()
    amenity = get_entity(all_amenities, amenity_id)
    storage.delete(amenity)
    storage.save()
    return jsonify({}), 200


def _post(amenity_id=None):
    ''' add amenity to storage '''
    data = request.get_json()
    if type(data) is not dict:
        raise BadRequest(description='Not a JSON')

    if 'name' not in data:
        raise BadRequest(description='Missing name')

    new_amenity = Amenity(**data)
    new_amenity.save()
    return jsonify(new_amenity.to_dict()), 201


def _put(amenity_id=None):
    ''' updates amenity with amenity_id '''
    xkeys = ('id', 'created_at', 'updated_at')
    all_amenities = storage.all(Amenity).values()
    amenity = get_entity(all_amenities, amenity_id)

    data = request.get_json()
    if type(data) is not dict:
        raise BadRequest(description='Not a JSON')

    for key, value in data.items():
        if key not in xkeys:
            setattr(amenity, key, value)
    amenity.save()
    return jsonify(amenity.to_dict()), 200
