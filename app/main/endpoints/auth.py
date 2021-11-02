import uuid
import base64
from flask import jsonify, after_this_request, request, g, session
from operator import itemgetter
from marshmallow import ValidationError
from datetime import datetime
from werkzeug.security import generate_password_hash
from app.main import main
from app.main.utils.auth import (
    generate_jwt_tokens,
    auth_guard,
    refresh_token,
    refresh_tokens_list
)
from app.schemas.schemas import SignUpSchema
from app.models.users import User
from app.crud.sql_model import sql_find


@main.route('/auth/signup', methods=['POST'])
def signup():
    # Check if schema of payload is correct
    try:
        payload = SignUpSchema().load(request.get_json())
    except ValidationError:
        return jsonify({
            'error': 'INVALID_SIGNUP_SCHEMA'
        }), 400

    firstName, lastName, email, password = itemgetter(
        'firstName',
        'lastName',
        'email',
        'password'
    )(payload)

    # Check if error is thrown or user already exists in database
    user_exists = sql_find(None, 'users', {'email': email})
    if 'error' in user_exists:
        return jsonify(user_exists), 400

    if len(user_exists['results']) > 0:
        return jsonify({
            'error': 'SIGNUP_USER_ALREADY_EXISTS'
        }), 400

    # Create user class and write to database
    new_user = User(
        str(uuid.uuid4()),
        0,
        None,
        None,
        None,
        None,
        firstName,
        lastName,
        email,
        generate_password_hash(password),
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    )

    entries = [new_user.get_class_attr_values()]
    results = new_user.sql_insert('users', entries)

    return jsonify({
        'message': 'SIGNUP_USER_SUCCESSFUL',
        'error': results['error'] if 'error' in results else None
    })


@main.route('/auth/login', methods=['GET'])
def login():
    # Check if user has already logged in
    # if 'is_logged_in' in session:
    #     return jsonify({
    #         'message': 'USER_ALREADY_LOGGED_IN'
    #     }), 400

    # Check if schema of payload is correct

    # try:
    #     payload = LoginSchema().load(request.get_json())
    # except ValidationError:
    #     return jsonify({
    #         'message': 'INVALID_LOGIN_SCHEMA'
    #     }), 400
    # email, password = itemgetter('email', 'password')(payload)

    credentials_bytes = base64.b64decode(request.headers.get('Authorization'))
    credentials = credentials_bytes.decode('utf-8').split(' ')[1]
    email = credentials.split(':')[0]
    password = credentials.split(':')[1]

    # Check if error is thrown or user exists in database
    user_exists = sql_find(None, 'users', {'email': email})
    if 'error' in user_exists:
        return jsonify(user_exists), 400

    if len(user_exists['results']) == 0:
        return jsonify({
            'error': 'LOGIN_USER_NOT_EXIST'
        }), 400

    # Create user model from query results
    # Check if password is correct
    logged_user = User(*user_exists['results'][0].values())
    check_password = logged_user.verify_password(password)

    if not check_password:
        return jsonify({
            'error': 'LOGIN_INVALID_PASSWORD'
        }), 400

    # Generate JWT if password is correct
    token_tuple = generate_jwt_tokens(
        logged_user._id,
        logged_user.firstName,
        logged_user.lastName,
        logged_user.email,
        False
    )

    session['is_logged_in'] = True

    @after_this_request
    def set_cookies(response):
        response.set_cookie(
            'access_token',
            token_tuple[0],
            max_age=3600,
            httponly=True
        )
        response.set_cookie(
            'refresh_token',
            token_tuple[1],
            max_age=3600,
            httponly=True
        )
        return response

    return jsonify({
        'message': 'LOGIN_SUCCESSFUL',
        'name': logged_user.firstName,
        'email': logged_user.email,
    })


@main.route('/refresh_token', methods=['GET'])
@refresh_token
@auth_guard
def refresh_token(new_access_token):
    @after_this_request
    def modify_cookies(response):
        response.delete_cookie('access_token')
        response.set_cookie(
            'access_token',
            new_access_token,
            max_age=3600,
            httponly=True
        )
        return response

    return jsonify({"message": "ACCESS_TOKEN_REFRESHED"})


@main.route('/logout', methods=['GET'])
@auth_guard
def logout():
    error_msg = None
    # Delete refresh token in server
    try:
        # Filter item in token_list if matches user_id and rmeove NULL
        del_item_list = list(filter(
            None,
            [item if item['_id'] == g.user_payload['sub']
                else None for item in refresh_tokens_list]
        ))
        if len(del_item_list) == 0:
            error_msg = 'NO_REFRESH_TOKEN_FOUND_IN_SERVER_STORAGE'
        else:
            refresh_tokens_list.remove(del_item_list[0])
    except ValueError as e:
        error_msg = 'DELETING_REFRESH_JWT, ValueError, {}'.format(e)
    except KeyError as e:
        error_msg = 'DELETING_REFRESH_JWT, KeyError, {}'.format(e)

    @after_this_request
    def delete_cookies(response):
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response

    if 'is_logged_in' in session:
        session.pop('is_logged_in')

    return jsonify({
        'message': 'LOGOUT_SUCCESS',
        'error': error_msg,
    })
