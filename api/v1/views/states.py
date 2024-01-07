#!/usr/bin/python3
'''
contains implementation of State routes:
    /states
    /states/<state_id>
'''

from api.v1.views import app_views, call_route_method,\
    get_entity, validate_data
from flask import jsonify, request
from models import storage
from models.state import State


ROUTE_METHODS = ['GET', 'DELETE', 'POST', 'PUT']


@app_views.route('/states', methods=ROUTE_METHODS)
@app_views.route('/states/<state_id>', methods=ROUTE_METHODS)
def handle_states(state_id=None):
    ''' handles routes relating to states '''
    handlers = {
        'GET': get_states,
        'DELETE': delete_state,
        'POST': post_state,
        'PUT': put_state,
    }

    return call_route_method(handlers, **{"state_id": state_id})


def get_states(state_id=None):
    ''' gets states or state based on state_id '''
    all_states = storage.all(State).values()
    state = get_entity(all_states, state_id)
    if state:
        return jsonify(state.to_dict())

    all_states = list(map(lambda x: x.to_dict(), all_states))
    return jsonify(all_states)


def delete_state(state_id=None):
    ''' deletes states with state_id '''
    all_states = storage.all(State).values()
    state = get_entity(all_states, state_id)
    storage.delete(state)
    storage.save()
    return jsonify({}), 200


def post_state(state_id=None):
    ''' adds new state to storage '''
    data = request.get_json()
    validate_data(data)
    new_state = State(**data)
    new_state.save()
    return jsonify(new_state.to_dict()), 201


def put_state(state_id=None):
    '''Updates the state with the given id.
    '''
    xkeys = ('id', 'created_at', 'updated_at')
    all_states = storage.all(State).values()
    state = get_entity(all_states, state_id, raiseException=True)
    data = request.get_json()
    validate_data(data, includeKey=False)
    for key, value in data.items():
        if key not in xkeys:
            setattr(state, key, value)
    state.save()
    return jsonify(state.to_dict()), 200
