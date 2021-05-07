import os
import re
from flask import (
    Flask, 
    request, 
    jsonify, 
    abort
)
from sqlalchemy import exc
import json
from flask_cors import (
    CORS,
    cross_origin
)
from werkzeug.exceptions import (
    InternalServerError,
    BadRequest,
    MethodNotAllowed,
    Unauthorized,
    Forbidden,
    NotFound
) 
from .database.models import (
    db_drop_and_create_all, 
    setup_db, 
    Drink
)
from .auth.auth import (
    AuthError, 
    requires_auth,
    get_required_auth
)
import logging 

logging.basicConfig(level=10)
app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
setup_db(app)
CORS(app, resources={r"/*": {"origins": "*"}})

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the 
        list of drinks or appropriate status code indicating reason for failure
'''
@app.route("/drinks")
def get_drinks():
    try:
        drinks = [d.short() for d in Drink.query.all()]
        return jsonify({
            "success": True,
            "drinks": drinks
        }), 200
    except InternalServerError:
        abort(500)
'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks-detail")
@requires_auth(permission="get:drinks-detail")
def get_drinks_detail(*args, **kwargs):
    try:
        drinks = [d.long() for d in Drink.query.all()]
        return jsonify({
            "success": True,
            "drinks": drinks
        }), 200
    except AuthError as e:
        abort(e.status_code, e.error)
    except BadRequest as e:
        abort(400, e.args)
    except Unauthorized as e:
        abort(401, e.args)
    except Forbidden as e:
        abort(403, e.args)
    except MethodNotAllowed as e:
        abort(405)
    except InternalServerError:
        abort(500)
    

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods=["POST"])
@requires_auth(permission="post:drinks")
def post_drinks(*args, **kwargs):
    payload = request.get_json()
    try:
        new_drink = Drink(
            title=payload.get("title"),
            recipe=json.dumps(payload.get("recipe"))
        )
        new_drink.insert()
        return jsonify({
            "success": True,
            "drinks": [new_drink.long()]
        }), 200
    except AuthError as e:
        abort(e.status_code, e.error)
    except BadRequest as e:
        abort(400, e.args)
    except Unauthorized as e:
        abort(401, e.args)
    except Forbidden as e:
        abort(403, e.args)
    except InternalServerError:
        abort(500)
    
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
@app.route("/drinks/<int:drink_id>", methods=["DELETE"])
@requires_auth(permission="delete:drinks")
def delete_drink(drink_id: int):
    try:
        drink_to_delete = Drink.query.get(drink_id)
        if drink_to_delete is None:
            raise NotFound("The requested resource has not been found.")
        drink_to_delete.delete()
        return jsonify({
            "success": True,
            "id": drink_id
        }), 200
    except AuthError as e:
        abort(e.status_code, e.error)
    except BadRequest as e:
        abort(400, e.args)
    except Unauthorized as e:
        abort(401, e.args)
    except Forbidden as e:
        abort(403, e.args)
    except NotFound as e:
        abort(404, e.args)
    except InternalServerError:
        abort(500)
    else:
        abort(500)

@app.route("/drinks/­<int:drink_id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def patch_drinks(drink_id: int):
    try:
        payload = request.get_json()
        drink_to_patch = Drink.query.get(drink_id)
                
        if drink_to_patch is None:
            raise NotFound(404, "The requested resource has not been found.")
                
        title = payload.get("title") 
        drink_to_patch.title = title if title is not None else drink_to_patch.title 
        drink_to_patch.recipe = json.dumps(payload.get("recipe"))
        drink_to_patch.update()
                
        return jsonify({
            "success": True,
            "drinks": drink_to_patch.long()
        }), 200
        
    except AuthError as e:
        abort(e.status_code, e.error)
    except BadRequest as e:
        abort(400, e.args)
    except Unauthorized as e:
        abort(401, e.args)
    except Forbidden as e:
        abort(403, e.args)
    except NotFound as e:
        abort(404, e.args)
    except MethodNotAllowed as e:
        abort(405, e.args)
    except InternalServerError:
        abort(500)
            
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
        "message": "Bad request"
    }), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Unauthorized"
    }), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "Forbidden"
    }), 403

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Not found"
    }), 404

@app.errorhandler(405)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "Method not allowed"
    }), 405

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal server error"
    }), 500
