from marshmallow import ValidationError
from flask import current_app, jsonify
from app.main import main


@main.errorhandler(ValidationError)
def validation_error(e):
    current_app.logger.error(e)
    return jsonify({
        'error': 'SCHEMA_VALIDATION_ERROR',
        'message': e
    }), 400


@main.errorhandler(400)
def bad_request_error(e):
    current_app.logger.error(e)
    return jsonify({
        'error': 'BAD_REQUEST',
        'message': e
    }), 400


@main.errorhandler(401)
def unauthorized_error(e):
    current_app.logger.error(e)
    return jsonify({
        'error': 'UNAUTHORIZED',
        'message': e
    }), 401


@main.errorhandler(403)
def forbidden_error(e):
    current_app.logger.error(e)
    return jsonify({
        'error': 'FORBIDDEN',
        'message': e
    }), 403


@main.errorhandler(404)
def endpoint_not_found_error(e):
    current_app.logger.error(e)
    return jsonify({
        'error': 'ENDPOINT_NOT_FOUND',
        'message': e
    }), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    current_app.logger.error(e)
    return jsonify({
        'error': 'INTERNAL_SERVER_ERROR',
        'message': e
    }), 500