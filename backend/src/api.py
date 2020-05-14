import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)

CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()
# set up CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


# ROUTES
'''
GET /drinks
'''
@app.route('/drinks')
def get_drinks():
    try:
        all_drinks = Drink.query.order_by(Drink.id).all()

        if len(all_drinks) == 0:
            abort(404)

        drinks = [{"title": drink.title, "recipe": json.loads(drink.recipe)}
                  for drink in all_drinks]

        return jsonify({
            'success': True,
            'drinks': drinks,
        }), 200
    except Exception:
        abort(422)


'''GET /drinks-detail'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drink_details(self):
    try:
        all_drinks = Drink.query.all()

        if len(all_drinks) == 0:
            abort(404)

        drinks = [drink.long() for drink in all_drinks]

        return jsonify({
            'success': True,
            'drinks': drinks,
        }), 200
    except Exception:
        abort(422)


'''POST /drinks'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def createdrink(payload):

    body = request.get_json()
    new_title = body.get('title', None)
    new_recipe = body.get('recipe', None)

    try:
        if body == {}:
            abort(400)

        drink = Drink(title=new_title, recipe=json.dumps(new_recipe))
        drink.insert()
        new_drink = [drink.long()]

        return jsonify({
            'success': True,
            'drinks': new_drink,
        }), 200
    except Exception:
        abort(422)


'''
PATCH /drinks/<id>
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):

    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if drink is None:
        abort(404)

    body = request.get_json()
    if body is None:
        abort(400)

    new_title = body.get('title', None)
    new_recipe = body.get('recipe', None)

    try:
        if new_title is not None:
            drink.title = new_title

        if new_recipe is not None:
            drink.recipe = json.dumps(new_recipe)

        drink.update()

        new_drink = [drink.long()]

        return jsonify({
            'success': True,
            'drinks': new_drink,
        }), 200

    except Exception:
        abort(422)


'''
DELETE /drinks/<id>
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(self, drink_id):

    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if drink is None:
        abort(404)
    drink.delete()

    return jsonify({
        'success': True,
        'delete': drink_id,
    }), 200


# Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400


'''
error handler for 404
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401


'''
error handler for AuthError
'''
@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "message": error.error
    }), error.status_code
