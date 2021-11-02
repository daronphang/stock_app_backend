from flask import Flask
from flask_cors import CORS
from config import config
from .main import main as main_blueprint

'''
Application factory for application package. \
Delays creation of an app by moving it into a factory function that can be \
explicitly invoked from script and apply configuration changes.
'''

cors = CORS(
    main_blueprint,
    origins=['http://127.0.0.1:4200', 'http://localhost:4200'],
    supports_credentials=True
)


def create_app(config_name):
    app = Flask(__name__)
    # Importing configuration settings directly into app
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Initializing extensions after app is created
    cors.init_app(app)

    # Manually creating app_context to access objects outside of view functions
    with app.app_context():
        app.register_blueprint(main_blueprint)

    return app
