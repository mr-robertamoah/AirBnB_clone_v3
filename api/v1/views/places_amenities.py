#!/usr/bin/python3
'''
contains routes regarding places' amenities and they are:
    /places/<place_id>/amenities
    /places/<place_id>/amenities/<amenity_id
'''

from api.v1.views import app_views, call_route_method,\
    get_entity, validate_data
from flask import jsonify, request
from models import storage, storage_t
from models.amenity import Amenity
from models.place import Place
from werkzeug.exceptions import NotFound, MethodNotAllowed


@app_views.route('/places/<place_id>/amenities', methods=['GET'])
@app_views.route(
    '/places/<place_id>/amenities/<amenity_id>',
    methods=['DELETE', 'POST']
)
def handle_places_amenities(place_id=None, amenity_id=None):
    ''' handle routes relating to place amenities '''
    handlers = {
        'GET': get_place_amenities,
        'DELETE': remove_place_amenity,
        'POST': add_place_amenity
    }

    args = {"place_id": place_id, "amenity_id": amenity_id}
    return call_route_method(handlers, **args)


def get_place_amenities(place_id=None, amenity_id=None):
    ''' get amenities relating to a place '''
    place = storage.get(Place, place_id)
    if place:
        raise NotFound()

    all_amenities = list(map(lambda x: x.to_dict(), place.amenities))
    return jsonify(all_amenities)


def remove_place_amenity(place_id=None, amenity_id=None):
    ''' deletes amenity from storage '''

    place = storage.get(Place, place_id)
    amenity = storage.get(Amenity, amenity_id)
    if not place or not amenity:
        raise NotFound()
    place_amenity_link = list(
        filter(lambda x: x.id == amenity_id, place.amenities)
    )
    if not place_amenity_link:
        raise NotFound()
    if storage_t == 'db':
        amenity_place_link = list(
            filter(lambda x: x.id == place_id, amenity.place_amenities)
        )
        if not amenity_place_link:
            raise NotFound()
        place.amenities.remove(amenity)
        place.save()
    else:
        amenity_idx = place.amenity_ids.index(amenity_id)
        place.amenity_ids.pop(amenity_idx)
        place.save()

    return jsonify({}), 200


def add_place_amenity(place_id=None, amenity_id=None):
    ''' add amenity to storage '''
    place = storage.get(Place, place_id)
    amenity = storage.get(Amenity, amenity_id)
    if not place or not amenity:
        raise NotFound()

    if storage_t == 'db':
        place_amenity_link = list(
            filter(lambda x: x.id == amenity_id, place.amenities)
        )
        amenity_place_link = list(
            filter(lambda x: x.id == place_id, amenity.place_amenities)
        )
        if amenity_place_link and place_amenity_link:
            res = amenity.to_dict()
            del res['place_amenities']
            return jsonify(res), 200
        place.amenities.append(amenity)
        place.save()
        res = amenity.to_dict()
        del res['place_amenities']
        return jsonify(res), 201
    else:
        if amenity_id not in place.amenity_ids:
            place.amenity_ids.push(amenity_id)
            place.save()
        return jsonify(amenity.to_dict()), 201
