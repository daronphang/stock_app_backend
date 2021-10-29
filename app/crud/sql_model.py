import inspect
from functools import wraps
from app.crud.utils.sql_connection import MySQLDBConnectionSession
from app.crud.utils.sql_string_formatter import (
    sql_insert_formatter,
    sql_query_formatter,
    sql_update_formatter
)


# Decorator for sql connection and cursor execution
def sql_connection(is_dict, error_msg):
    def inner_decorator(f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            with MySQLDBConnectionSession(is_dict) as conn:
                try:
                    cursor = conn.cursor(dictionary=is_dict)
                    results = f(self, cursor, *args, **kwargs)
                    conn.commit()
                    return results
                except Exception as e:
                    conn.rollback()
                    return {
                        'message': error_msg,
                        'error': str(e)
                    }
        return wrapper
    return inner_decorator


# QUERY method, allows multiple queries
# Query key/values in dict format
@sql_connection(True, 'INVALID TABLE OR QUERY KEY')
def sql_find(self, cursor, table: str, query: dict):
    sql_string, values = sql_query_formatter(table, query)
    cursor.execute(sql_string, tuple(values))
    return {
        'message': 'QUERY SUCCESSFUL',
        'results': cursor.fetchall()
        }


class SQLMixin(object):
    # Retrieve class attributes of current instance
    def get_class_attr(self):
        return str(inspect.signature(self.__class__))

    # Retrieve class attribute values of current instance
    def get_class_attr_values(self):
        return tuple(self.__dict__.values())

    # INSERT method, allows inserting multiple rows
    # entries argument is a list of tuple values
    @sql_connection(False, 'INVALID TABLE, TABLE COLUMN OR ENTRY')
    def sql_insert(self, cursor, table: str, entries: list):
        cols = str(inspect.signature(self.__class__))
        sql_string = sql_insert_formatter(table, cols, entries)
        placeholder = [value for entry in entries for value in entry]
        cursor.execute(sql_string, tuple(placeholder))
        return {
            'message': 'INSERT SUCCESSFUL'
        }

    @sql_connection(False, 'INVALID TABLE, TABLE COLUMN OR ENTRY')
    def sql_update(self, cursor, table: str, update_fields: str, query: dict):
        sql_string, values = sql_update_formatter(table, update_fields, query)
        cursor.execute(sql_string, tuple(values))
        return {
            'message': 'UPDATE SUCCESSFUL'
        }