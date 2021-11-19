import logging
import mysql.connector as mysql
from flask import current_app

logger = logging.getLogger(__name__)


class MySQLDBConnectionSession:
    def __init__(self, is_dict: bool):
        self.conn = mysql.connect(
            host=current_app.config['MYSQL_HOST'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=current_app.config['MYSQL_DATABASE'],
            port=current_app.config['MYSQL_PORT']
        )
        self.is_dict = is_dict

    def __enter__(self):
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.conn.close()
