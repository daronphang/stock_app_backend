import jwt
from functools import wraps
from flask import request, jsonify, current_app, g
from datetime import datetime, timedelta

# Server-side storage of refresh tokens
# dict {'_id': _id, 'refresh_token': token}
refresh_tokens_list = []


def generate_jwt_tokens(_id, first_name, last_name, email):
    headers = {
        'alg': 'HS256',
        'typ': 'JWT'
    }

    payload = {
        "sub": _id,
        "name": ' '.join([first_name, last_name]),
        "email": email,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=60)
    }

    access_token = jwt.encode(
            payload=payload,
            key=current_app.config['SECRET_KEY'],
            algorithm='HS256',
            headers=headers
    )

    refresh_token = jwt.encode(
            payload=payload,
            key=current_app.config['REFRESH_SECRET_KEY'],
            algorithm='HS256',
            headers=headers
    )

    # Store refresh tokens in server for future validation
    refresh_tokens_list.append(
        {'_id': _id, 'refresh_token': refresh_token}
    )
    return access_token, refresh_token


def auth_guard(f):
    '''
    Authentication decorator to be added for every protected route. Client \
    provides token in authentication header. Checks if the token provided by \
    client is valid and sets user payload data in global g dict.

    @wraps helps to preserve the function used in decorator and adds \
    functionality of copying over function name, docstring, etc. Helps \
    to preserve function's metadata.
    '''
    @wraps(f)
    def check_access_token(*args, **kwargs):
        token = request.cookies.get('access_token')
        if not token:
            return jsonify({
                'message': 'NO_ACCESS_TOKEN_FOUND_IN_COOKIE'
            }), 401

        try:
            user_payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                'HS256'
            )

            g.user_payload = user_payload

        except jwt.InvalidTokenError:
            return jsonify({
                'message': 'INVALID_ACCESS_TOKEN'
            }), 401

        except jwt.ExpiredSignatureError:
            return jsonify({
                'message': 'EXPIRED_ACCESS_TOKEN'
            }), 401
        finally:
            return f(*args, **kwargs)

    return check_access_token
