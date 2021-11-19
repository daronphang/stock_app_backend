import jwt
from functools import wraps
from flask import request, current_app, g
from datetime import datetime, timedelta
from app.main.errors import unauthorized_error, forbidden_error

# Server-side storage of refresh tokens
# dict {'_id': _id, 'refresh_token': token}
refresh_tokens_list = []


def generate_jwt_tokens(_id, first_name, last_name, email, isRefresh):
    headers = {
        'alg': 'HS256',
        'typ': 'JWT'
    }

    payload = {
        "sub": _id,
        "first_name": first_name,
        "last_name": last_name,
        "full_name": ' '.join([first_name, last_name]),
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

    if isRefresh:
        return access_token

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
            return unauthorized_error('NO_ACCESS_TOKEN_FOUND_IN_COOKIE')

        try:
            user_payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                'HS256'
            )

            g.user_payload = user_payload

        except jwt.InvalidTokenError:
            return unauthorized_error('INVALID_ACCESS_TOKEN')

        except jwt.ExpiredSignatureError:
            return unauthorized_error('EXPIRED_ACCESS_TOKEN')

        finally:
            return f(*args, **kwargs)

    return check_access_token


def refresh_token(f):
    @wraps(f)
    def refresh_token_handler(*args, **kwargs):
        token = request.cookies.get('refresh_token')
        if not token:
            return unauthorized_error('NO_REFRESH_TOKEN_FOUND_IN_COOKIE')

        try:
            # Check if refresh token is valid
            user_payload = jwt.decode(
                token,
                current_app.config['REFRESH_SECRET_KEY'],
                'HS256'
            )

            # Check if refresh token exists in server database
            # Needed if admin revoke refresh_token rights
            list = [
                True if token_obj['refresh_token'] == token else False
                for token_obj in refresh_tokens_list
            ]

            if True not in list:
                return forbidden_error('REFRESH_TOKEN_NOT_FOUND_IN_SERVER')

            # Refresh token is valid; to regenerate access token
            new_access_token = generate_jwt_tokens(
                user_payload['sub'],
                user_payload['first_name'],
                user_payload['last_name'],
                user_payload['email'],
                True
            )
            return f(new_access_token, *args, **kwargs)

        except jwt.InvalidTokenError:
            return unauthorized_error('INVALID_REFRESH_TOKEN')

        except jwt.ExpiredSignatureError:
            return unauthorized_error('EXPIRED_REFRESH_TOKEN')

    return refresh_token_handler
