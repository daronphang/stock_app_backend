import uuid
import base64
from flask import jsonify, after_this_request, request, g, session
from operator import itemgetter
from marshmallow import ValidationError
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
from app.main.errors import (
    forbidden_error,
    internal_server_error,
    validation_error,
    unauthorized_error,
)


@main.route('/auth/signup', methods=['POST'])
def signup():
    # Check if schema of payload is correct
    try:
        payload = SignUpSchema().load(g.request_payload)
    except ValidationError:
        return validation_error('SIGNUP_SCHEMA_INVALID')

    firstName, lastName, email, password = itemgetter(
        'firstName',
        'lastName',
        'email',
        'password'
    )(payload)

    # Create new user
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
        # datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        # datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    )

    rv = new_user.signup()
    if 'error' in rv:
        return internal_server_error(rv['error'])
    if rv['message'] == 'USER_EXISTS':
        return forbidden_error('SIGNUP_USER_ALREADY_EXISTS')
    return jsonify(rv)


@main.route('/auth/login', methods=['GET'])
def login():
    # Check if user has already logged in
    # if 'is_logged_in' in session:
    #     return jsonify({
    #         'message': 'USER_ALREADY_LOGGED_IN'
    #     }), 400

    # Check if schema of payload is correct

    # For Postman
    # credentials_bytes = base64.b64decode(
    #     request.headers.get('Authorization').split(' ')[1]
    # )
    # credentials = credentials_bytes.decode('utf-8')
    # email = credentials.split(':')[0]
    # password = credentials.split(':')[1]

    # For Chrome
    credentials_bytes = base64.b64decode(
        request.headers.get('Authorization')
    )
    credentials = credentials_bytes.decode('utf-8')
    email = credentials.split(' ')[1].split(':')[0]
    password = credentials.split(' ')[1].split(':')[1]

    # Check if error is thrown while executing query
    user_exists = sql_find(None, '*', 'users', {'email': email})
    if 'error' in user_exists:
        return internal_server_error(user_exists['error'])

    # Check if user does not exist in database
    if user_exists['row_count'] == 0:
        return unauthorized_error('LOGIN_USER_NOT_EXIST')

    # Create user model from query results
    # Check if password is correct
    user_values = list(user_exists['results'][0].values())
    # remove createdAt and updatedAt fields
    del user_values[-2:]
    logged_user = User(*user_values)
    check_password = logged_user.verify_password(password)

    if not check_password:
        return unauthorized_error('LOGIN_INVALID_PASSWORD')

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
