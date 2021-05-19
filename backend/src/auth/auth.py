import json
from flask import request 
from functools import wraps
from jose import jwt
from urllib.request import urlopen
from typing import Any

AUTH0_DOMAIN = 'secure-app-trust-me.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'http://localhost:5000'


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_token_auth_header():
    auth_token = request.headers.get("Authorization") 
    if auth_token is None:
        raise AuthError("No Authorization header provided", 401)
    token = auth_token.split(sep=" ")
    if len(token) != 2 or token[0].lower() != "bearer":
        raise AuthError("Authorization header malformed", 400)
    return token[1]
   

def check_permissions(permission, payload):
    if not "permissions" in payload:
        raise AuthError(
            "Bad request: Permissions are not included in JWT.",
            400
        )
    permission_checked = permission in [el.lower() for el in payload.get("permissions")]
    if not permission_checked:
        raise AuthError(
            "Forbidden: you do not have the authorization to access the requested resource.", 
            403
        )
    return True

        
def verify_decode_jwt(token):
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'Invalid Header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(token,
                                 rsa_key,
                                 algorithms=ALGORITHMS,
                                 audience=API_AUDIENCE,
                                 issuer=f"https://{AUTH0_DOMAIN}/")
            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                "code": "Expired token",
                "description": "Expired token."
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                "code": "Invalid claims",
                "description": "Incorrect claims. Please, check the audience and issuer."
            }, 401)
        except Exception:
            raise AuthError({
                "code": "Invalid header",
                "description": "Unable to parse authentication token."
            }, 400)
    

def requires_auth(permission: Any):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            if payload is None:
                raise AuthError("Unauthorized", 401)
            check_permissions(permission, payload)
            return f(*args, **kwargs)
        return wrapper
    return requires_auth_decorator
