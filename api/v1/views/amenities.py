#!/usr/bin/python3
'''
Contains the amenities routes:
    /amenities
    /amenities/<amenity_id>
'''

from api.v1.views import app_views, call_route_method,\
    get_entity, validate_data
from flask import jsonify, request
from models import storage
from models.amenity import Amenity


ROUTE_METHODS = ['GET', 'DELETE', 'POST', 'PUT']


@app_views.route('/amenities', methods=ROUTE_METHODS)
@app_views.route('/amenities/<amenity_id>', methods=ROUTE_METHODS)
def handle_amenities(amenity_id=None):
    ''' handles routes relating to amenities '''
    handlers = {
        'GET': get_amenities,
        'DELETE': delete_amenity,
        'POST': post_amenity,
        'PUT': put_amenity,
    }

    return call_route_method(handlers, **{"amenity_id": amenity_id})


def get_amenities(amenity_id=None):
    ''' gets amenity with the given amenity_id or all amenities '''
    all_amenities = storage.all(Amenity).values()
    amenity = get_entity(all_amenities, amenity_id)
    if amenity:
        return jsonify(amenity.to_dict())

    all_amenities = list(map(lambda x: x.to_dict(), all_amenities))
    return jsonify(all_amenities)


def delete_amenity(amenity_id=None):
    ''' deletes amenity with given amenity_id '''
    all_amenities = storage.all(Amenity).values()
    amenity = get_entity(all_amenities, amenity_id, raiseException=True)
    storage.delete(amenity)
    storage.save()
    return jsonify({}), 200


def post_amenity(amenity_id=None):
    ''' add amenity to storage '''
    data = request.get_json()
    validate_data(data)
    new_amenity = Amenity(**data)
    new_amenity.save()
    return jsonify(new_amenity.to_dict()), 201


def put_amenity(amenity_id=None):
    ''' updates amenity with amenity_id '''
    xkeys = ('id', 'created_at', 'updated_at')
    all_amenities = storage.all(Amenity).values()
    amenity = get_entity(all_amenities, amenity_id)

    data = request.get_json()
    validate_data(data, includeKey=False)
    for key, value in data.items():
        if key not in xkeys:
            setattr(amenity, key, value)
    amenity.save()
    return jsonify(amenity.to_dict()), 200
