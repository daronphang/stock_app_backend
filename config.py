import os
import logging
from flask import request, g

basedir = os.path.abspath(os.path.dirname(__file__))


# Default logs value of '%(message)s'
# Converts LogRecord to formatted string
class RequestFormatter(logging.Formatter):
    # Appends datetime, stack and exception if called
    def format(self, record):
        record.username = g.user_payload['email'] \
            if hasattr(g, 'user_payload') else request.remote_addr
        return super().format(record)


class Config:
    BASEDIR = basedir
    PROJECT_NAME = "Daron's Stock Screener"
    SECRET_KEY = os.environ.get('SECRET_KEY')
    REFRESH_SECRET_KEY = os.environ.get('REFRESH_SECRET_KEY')
    MYSQL_HOST = os.environ.get('MYSQL_HOST')
    MYSQL_USER = os.environ.get('MYSQL_USER')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE')
    MYSQL_PORT = os.environ.get('MYSQL_PORT')
    # SQLALCHEMY_TRACK_MODIFCATIONS = False
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL')


class TestingConfig(Config):
    TESTING = TrueWTF_CSRF_ENABLED = False

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        import logging
        from flask.logging import default_handler

        app.logger.removehandler(default_handler)
        app.logger.setLevel(logging.INFO)
        formatter = RequestFormatter(
            '[%(asctime)s] %(username)s %(levelname)s in %(module)s: '
            '%(message)s'
        )
        logfile_handler = logging.FileHandler(
            os.path.join(cls.BASEDIR, f'{cls.PROJECT_NAME}.log')
        )
        logfile_handler.setFormatter(formatter)
        logfile_handler.setLevel(logging.INFO)
        app.logger.addHandler(logfile_handler)


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        import logging
        from flask.logging import default_handler

        app.logger.removehandler(default_handler)
        app.logger.setLevel(logging.INFO)
        formatter = RequestFormatter(
            '[%(asctime)s] %(username)s %(levelname)s in %(module)s: '
            '%(message)s'
        )
        logfile_handler = logging.RotatingFileHandler(
            os.path.join(cls.BASEDIR, f'{cls.PROJECT_NAME}.log'),
            maxBytes=1024000,
            backupCount=10,
            encoding='utf-8'
        )
        logfile_handler.setFormatter(formatter)
        logfile_handler.setLevel(logging.INFO)
        app.logger.addHandler(logfile_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}