#!/usr/bin/python3
'''
contains the cities routes:
    /states/<state_id>/cities
    /cities/<city_id>
'''

from api.v1.views import app_views, call_route_method,\
    get_entity, validate_data
from flask import jsonify, request
from models import storage, storage_t
from models.city import City
from models.place import Place
from models.review import Review
from models.state import State
from werkzeug.exceptions import MethodNotAllowed, NotFound, BadRequest


@app_views.route('/states/<state_id>/cities', methods=['GET', 'POST'])
@app_views.route('/cities/<city_id>', methods=['GET', 'DELETE', 'PUT'])
def handle_cities(state_id=None, city_id=None):
    ''' handles routes relating to cities '''
    handlers = {
        'GET': get_cities,
        'DELETE': delete_city,
        'POST': post_city,
        'PUT': put_city,
    }

    args = {"state_id": state_id, "city_id": city_id}
    return call_route_method(handlers, **args)


def get_cities(state_id=None, city_id=None):
    ''' get city with id or cities in a state '''
    if state_id:
        state = storage.get(State, state_id)
        if state:
            cities = list(map(lambda x: x.to_dict(), state.cities))
            return jsonify(cities)
    elif city_id:
        city = storage.get(City, city_id)
        if city:
            return jsonify(city.to_dict())
    raise NotFound()


def delete_city(state_id=None, city_id=None):
    ''' deletes city with city_id '''
    city = storage.get(City, city_id)
    if city:
        storage.delete(city)
        if storage_t != "db":
            for place in storage.all(Place).values():
                if place.city_id == city_id:
                    for review in storage.all(Review).values():
                        if review.place_id == place.id:
                            storage.delete(review)
                    storage.delete(place)
        storage.save()
        return jsonify({}), 200
    raise NotFound()


def post_city(state_id=None, city_id=None):
    ''' creates city and adds to state '''
    state = storage.get(State, state_id)
    if state is None:
        raise NotFound()

    data = request.get_json()
    validate_data(data)

    data['state_id'] = state_id
    city = City(**data)
    city.save()
    return jsonify(city.to_dict()), 201


def put_city(state_id=None, city_id=None):
    ''' updates city with city_id '''
    xkeys = ('id', 'state_id', 'created_at', 'updated_at')
    city = storage.get(City, city_id)
    if city:
        data = request.get_json()
        validate_data(data, includeKey=False)

        for key, value in data.items():
            if key not in xkeys:
                setattr(city, key, value)
        city.save()
        return jsonify(city.to_dict()), 200
    raise NotFound()
