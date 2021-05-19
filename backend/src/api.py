from flask import (
    Flask, 
    request, 
    jsonify, 
    abort
)
from sqlalchemy import exc
import json
from flask_cors import CORS
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
    requires_auth
)
from os import getenv
import logging 


class FallbackCFG:
    FLASK_CONFIG = "src.config.Development"
    APP_SETTINGS = "config.py"


fallback = FallbackCFG()
app = Flask(__name__)
app.config.from_object(fallback.FLASK_CONFIG)
app.config.from_envvar(fallback.APP_SETTINGS)
setup_db(app)
CORS(app, resources={r"/*": {"origins": "*"}})


db_drop_and_create_all()


## ROUTES
@app.route("/drinks")
def get_drinks():
    try:
        drinks = [d.short() for d in Drink.query.all()]
        return jsonify(
            {
                "success": True,
                "drinks": drinks
            }
        ), 200
    except InternalServerError:
        abort(500)


@app.route("/drinks-detail")
@requires_auth(permission="get:drinks-detail")
def get_drinks_detail():
    try:
        drinks = [d.long() for d in Drink.query.all()]
        return jsonify(
            {
                "success": True,
                "drinks": drinks
            }
        ), 200
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
    

@app.route("/drinks", methods=["POST"])
@requires_auth(permission="post:drinks")
def post_drinks():
    payload = request.get_json()
    try:
        new_drink = Drink(
            title=payload.get("title"),
            recipe=json.dumps(payload.get("recipe"))
        )
        new_drink.insert()
        return jsonify(
            {
                "success": True,
                "drinks": [new_drink.long()]
            }
        ), 200
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
    

@app.route("/drinks/<int:drink_id>", methods=["DELETE", "PATCH"])
def delete_or_patchdrink(drink_id: int):
    try:
        drink = Drink.query.get(drink_id)

        if request.method == "DELETE":
        
            @requires_auth(permission="delete:drinks")
            def delete():
                drink = Drink.query.get(drink_id)
        
                if drink is None:
                    raise NotFound("The requested resource has not been found.")
        
                drink.delete()
                return jsonify(
                    {
                        "success": True,
                        "id": drink_id
                    }
                ), 200

            return delete()

        elif request.method == "PATCH":

            @requires_auth(permission="patch:drinks")
            def patch():
                if drink is None:
                    raise NotFound("The requested resource has not been found.")

                payload = request.get_json()   
                title = payload.get("title") 
                drink.title = title if title is not None else drink.title 
                drink.recipe = json.dumps(payload.get("recipe"))
                drink.update()            

                return jsonify(
                    {
                        "success": True,
                        "drinks": drink.long()
                    }
                ), 200

            return patch()

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
    except Exception:
        abort(500)
    

@app.errorhandler(422)
def unprocessable(error):
    return jsonify(
        {
            "success": False, 
            "error": 422,
            "message": "unprocessable"
        }
    ), 422


@app.errorhandler(400)
def bad_request(error):
    return jsonify(
        {
            "success": False,
            "error": 400,
            "message": "Bad request"
        }
    ), 400


@app.errorhandler(401)
def unauthorized(error):
    return jsonify(
        {
            "success": False,
            "error": 401,
            "message": "Unauthorized"
        }
    ), 401


@app.errorhandler(403)
def forbidden(error):
    return jsonify(
        {
            "success": False,
            "error": 403,
            "message": "Forbidden"
        }
    ), 403


@app.errorhandler(404)
def not_found(error):
    return jsonify(
        {
            "success": False,
            "error": 404,
            "message": "Not found"
        }
    ), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify(
        {
            "success": False,
            "error": 405,
            "message": "Method not allowed"
        }
    ), 405


@app.errorhandler(500)
def internal_server_error(error):
    error_type = {
        400: bad_request,
        401: unauthorized,
        403: forbidden,
        404: not_found,
        405: method_not_allowed  
    }.get(error.status_code if 'status_code' in dir(error) else 999)
    
    if error_type is not None:
        return error_type(error)
    
    return jsonify(
        {
            "success": False,
            "error": 500,
            "message": "Internal server error"        
        }
    ), 500
