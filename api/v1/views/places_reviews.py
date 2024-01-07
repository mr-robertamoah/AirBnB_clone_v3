#!/usr/bin/python3
'''Contains the places_reviews view for the API.'''

from api.v1.views import app_views, call_route_method,\
get_entity, validate_data
from flask import jsonify, request
from models import storage
from models.place import Place
from models.review import Review
from models.user import User
from werkzeug.exceptions import NotFound, MethodNotAllowed, BadRequest


@app_views.route('/places/<place_id>/reviews', methods=['GET', 'POST'])
@app_views.route('/reviews/<review_id>', methods=['GET', 'DELETE', 'PUT'])
def handle_reviews(place_id=None, review_id=None):
    ''' handle routes relating to reviews '''
    handlers = {
        'GET': get_reviews,
        'DELETE': remove_review,
        'POST': add_review,
        'PUT': update_review
    }

    args = {"place_id": place_id, "review_id": review_id}
    return call_route_method(handlers, **args)


def get_reviews(place_id=None, review_id=None):
    ''' get reviews of place based on review_id '''
    place = storage.get(Place, place_id)
    if place:
        reviews = []
        for review in place.reviews:
            reviews.append(review.to_dict())
        return jsonify(reviews)
    review = storage.get(Review, review_id)
    if review:
        return jsonify(review.to_dict())

    raise NotFound()


def remove_review(place_id=None, review_id=None):
    ''' delete review from storage '''
    review = storage.get(Review, review_id)
    if not review:
        raise NotFound()

    storage.delete(review)
    storage.save()
    return jsonify({}), 200


def add_review(place_id=None, review_id=None):
    ''' add review to storage '''
    place = storage.get(Place, place_id)
    if not place:
        raise NotFound()

    data = request.get_json()
    validate_data(data, key=['user_id', 'text'])
    user = storage.get(User, data['user_id'])
    if not user:
        raise NotFound()

    data['place_id'] = place_id
    new_review = Review(**data)
    new_review.save()
    return jsonify(new_review.to_dict()), 201


def update_review(place_id=None, review_id=None):
    '''Updates the review with the given id.
    '''
    xkeys = ('id', 'user_id', 'place_id', 'created_at', 'updated_at')
    review = storage.get(Review, review_id)
    if not review:
        raise NotFound()

    data = request.get_json()
    validate_data(data, includeKey=False)
    for key, value in data.items():
        if key not in xkeys:
            setattr(review, key, value)
    review.save()
    return jsonify(review.to_dict()), 200
