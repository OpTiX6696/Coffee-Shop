from crypt import methods
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


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks')
def get_drinks():
    
    try:
        drinks = Drink.query.all()
        f_drinks = [drink.short() for drink in drinks]
        print("Gotten")
    except:
        abort(422)
        
    return jsonify({
        "success": True,
        "drinks": f_drinks
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    
    # return "Trial"
    try:
        drinks = Drink.query.all()
        f_drinks = [drink.long() for drink in drinks]
        print(f_drinks)
    except:
        abort(422)
        
    return jsonify({
        "success": True,
        "drinks": f_drinks
    })
    

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink(payload):
    try:
        data = request.get_json()
        title = data.get('title')
        recipe = json.dumps(data.get('recipe'))

        if (not title) or (not recipe):
            abort(400)
            
        new_drink = Drink(title=title, recipe=recipe)
        new_drink.insert()
    except:
        abort(422)
    return jsonify({"success": True, "drinks": new_drink.long()})
    

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(payload, id):
    
    drink = Drink.query.get(id)
    data = request.get_json()
    new_title = data.get('title')
    print(new_title)
    if (not new_title) or (not drink):
        abort(400)
        
    drink.title = new_title
    drink.update()
        
    return jsonify({
        "success": True,
        "drinks": list(drink.long())
    })

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=["DELETE"])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    
    drink = Drink.query.get(id)
    if not drink:
        abort(404)

    drink.delete()
    
    return jsonify({
        "success": True,
        "delete": id
    })
    
    
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


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

@app.errorhandler(AuthError)
def auth_errorhandler(arg):
    res = jsonify(arg.error)
    res.status_code = arg.status_code
    
    return res


