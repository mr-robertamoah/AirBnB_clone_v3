#!/usr/bin/python3
'''
contains implementation of routes relating to places and they are:
    /places/<place_ud>
    cities/<city_id>/places
'''

from api.v1.views import app_views, call_route_method,\
get_entity, validate_data, remove_keys
from flask import jsonify, request
from models import storage, storage_t
from models.amenity import Amenity
from models.city import City
from models.place import Place
from models.state import State
from models.user import User
from werkzeug.exceptions import NotFound, MethodNotAllowed, BadRequest


@app_views.route('/cities/<city_id>/places', methods=['GET', 'POST'])
@app_views.route('/places/<place_id>', methods=['GET', 'DELETE', 'PUT'])
def handle_places(city_id=None, place_id=None):
    ''' handles routes relating to places '''

    handlers = {
        'GET': get_places,
        'DELETE': delete_place,
        'POST': post_place,
        'PUT': put_place
    }
    args = {"city_id": city_id, "place_id": place_id}
    return call_route_method(handlers, **args)


def get_places(city_id=None, place_id=None):
    ''' gets place with place_id or places in a city '''
    city = storage.get(City, city_id)
    if city:
        all_places = []
        if storage_t == 'db':
            all_places = list(city.places)
        else:
            all_places = list(filter(
                lambda x: x.city_id == city_id,
                storage.all(Place).values()
            ))
        all_places = list(map(lambda x: x.to_dict(), all_places))
        return jsonify(all_places)
    place = storage.get(Place, place_id)
    if place:
        return jsonify(place.to_dict())
    raise NotFound()


def delete_place(city_id=None, place_id=None):
    ''' deletes place with place_id '''
    place = storage.get(Place, place_id)
    if place is None:
        raise NotFound()

    storage.delete(place)
    storage.save()
    return jsonify({}), 200


def post_place(city_id=None, place_id=None):
    ''' adds place to storage and attaches to city '''
    city = storage.get(City, city_id)
    if not city:
        raise NotFound()

    data = request.get_json()
    validate_data(data, ['name', 'user_id'])
    user = storage.get(User, data['user_id'])
    if not user:
        raise NotFound()

    data['city_id'] = city_id
    new_place = Place(**data)
    new_place.save()
    return jsonify(new_place.to_dict()), 201


def put_place(city_id=None, place_id=None):
    ''' updates place with place_id '''
    xkeys = ('id', 'user_id', 'city_id', 'created_at', 'updated_at')
    place = storage.get(Place, place_id)
    if place is None:
        raise NotFound()
    data = request.get_json()
    if type(data) is not dict:
        raise BadRequest(description='Not a JSON')
    for key, value in data.items():
        if key not in xkeys:
            setattr(place, key, value)
    place.save()
    return jsonify(place.to_dict()), 200


@app_views.route('/places_search', methods=['POST'])
def find_places():
    '''Finds places based on a list of State, City, or Amenity ids.
    '''
    data = request.get_json()
    validate(data, includeKey=False)
    all_places = storage.all(Place).values()
    places = []
    places_id = []
    keys_status = (
        all([
            'states' in data and type(data['states']) is list,
            'states' in data and len(data['states'])
        ]),
        all([
            'cities' in data and type(data['cities']) is list,
            'cities' in data and len(data['cities'])
        ]),
        all([
            'amenities' in data and type(data['amenities']) is list,
            'amenities' in data and len(data['amenities'])
        ])
    )
    if keys_status[0]:
        for state_id in data['states']:
            if not state_id:
                continue
            state = storage.get(State, state_id)
            if not state:
                continue
            _places = get_places_from_cities(data['cities'], place_ids)
            places.extend(_places)
            places_id.extend(list(map(lambda x: x.id, _places)))
    if keys_status[1]:
        places.extend(get_places_from_cities(data['cities'], place_ids, ids=True))
    del places_id

    if all([not keys_status[0], not keys_status[1]]) or not data:
        places = all_places
    if keys_status[2]:
        amenity_ids = []
        for amenity_id in data['amenities']:
            if not amenity_id:
                continue
            amenity = storage.get(Amenity, amenity_id)
            if amenity and amenity.id not in amenity_ids:
                amenity_ids.append(amenity.id)
        del_indices = []
        for place in places:
            place_amenities_ids = list(map(lambda x: x.id, place.amenities))
            if not amenity_ids:
                continue
            for amenity_id in amenity_ids:
                if amenity_id not in place_amenities_ids:
                    del_indices.append(place.id)
                    break
        places = list(filter(lambda x: x.id not in del_indices, places))
    result = []
    for place in places:
        obj = remove_keys(place.to_dict(), ['amenities'])
        result.append(obj)
    return jsonify(result)


def get_places_from_cities(cities, place_id, ids=False):
    ''' get places from city ids '''
    places = []
    if ids:
        cities = list(map(lambda x: storage.get(City, x), cities))
    for city_id in cities:
        if not city:
            continue
        if storage_t == 'db':
            places.extend(list(
                filter(lambda x: x.id not in places_id, city.places)
            ))
        else:
            places = []
            for place in all_places:
                if place.id not in places_id and place.city_id == city.id:
                    places.append(place)
    return places
