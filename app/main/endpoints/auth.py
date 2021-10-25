import uuid
from flask import jsonify, after_this_request, request
from operator import itemgetter
from marshmallow import ValidationError
from datetime import datetime
from app.main import main
from app.main.utils.auth import generate_jwt_tokens, auth_guard
from app.schemas.schemas import SignUpSchema
from app.models.users import User


@main.route('/auth/signup', methods=['POST'])
def signup():
    try:
        payload = SignUpSchema().load(request.get_json())
    except ValidationError:
        return jsonify({
            'message': 'INVALID_SIGNUP_SCHEMA'
        }), 400

    firstName, lastName, email, password = itemgetter(
        'firstName',
        'lastName',
        'email',
        'password'
    )(payload)

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
        password,
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    )

    cols = new_user.get_class_attr()
    entries = [new_user.get_class_attr_values(new_user)]
    results = new_user.sql_insert('users', cols, entries)
    # results = new_user.sql_find('users', {
    #     'email': 'admin@gmail.com',
    #     '_id': 'ec57217c-74b9-45d9-8f59-b7b47576fb45'
    # })

    response = jsonify({
        'message': results['message'],
        'results': results['results'] if 'results' in results else None,
        'error': results['error'] if 'error' in results else None
    })

    return response


@main.route('/auth/login', methods=['POST'])
def login():
    token_tuple = generate_jwt_tokens(
        123,
        'daron',
        'phang',
        'daronphang@gmail.com'
    )

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

    return jsonify({'message': ' hello world!'})


@main.route('/logout', methods=['GET'])
@auth_guard
def logout():
    return jsonify({
        'message': 'LOGOUT_SUCCESS'
    })
