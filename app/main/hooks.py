from datetime import datetime
from flask import g, request, _request_ctx_stack, current_app
from app.main import main


@main.before_request
def set_global_variable():
    g.request_timestamp = datetime.utcnow()
    g.payload = request.json if request.json else None


@main.after_request
def log_request(response):
    ctx = _request_ctx_stack.top
    request_duration = (datetime.utcnow() - g.request_timestamp) \
        .total_seconds()

    info = {
        'url': ctx.request.url,
        'method': ctx.request.method,
        'server_name': ctx.app.name,
        'blueprint': ctx.request.blueprint,
        'view_args': ctx.request.view_args,
        'status': response.status_code,
        'speed': float(request_duration),
        'payload': g.payload,
        'service_name': current_app.config['PROJECT_NAME']
    }
    current_app.logger.info(f'after request logging: {info}')
    return response
