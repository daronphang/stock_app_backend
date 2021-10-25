import inspect
from functools import wraps
from app.crud.utils.sql_connection import MySQLDBConnectionSession
from app.crud.utils.sql_string_formatter import sql_insert_formatter, \
    sql_query_formatter


# Decorator for sql connection and cursor execution
def sql_connection(is_dict, error_msg):
    def inner_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            with MySQLDBConnectionSession(is_dict) as conn:
                try:
                    cursor = conn.cursor(dictionary=is_dict)
                    results = f(cursor, *args, **kwargs)
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


class SQLMixin(object):
    # Retrieve class attributes of current instance
    def get_class_attr(self):
        return str(inspect.signature(self.__class__))

    # Retrieve class attribute values of current instance
    def get_class_attr_values(self, instance):
        attr = str(inspect.signature(self.__class__))
        attr_list = attr[1:-1].split(', ')
        values = tuple(map(lambda x: getattr(instance, x), attr_list))
        return values

    # QUERY method; allows multiple query key/values
    @staticmethod
    @sql_connection(True, 'INVALID TABLE OR QUERY KEY')
    def sql_find(cursor, table: str, query: dict):
        sql_string = sql_query_formatter(table, query)
        cursor.execute(sql_string, tuple(query.values()))
        return {
            'message': 'QUERY SUCCESSFUL',
            'results': cursor.fetchall()
        }

    # INSERT method; allows inserting multiple rows
    @staticmethod
    @sql_connection(False, 'INVALID TABLE, TABLE COLUMN OR ENTRY')
    def sql_insert(cursor, table: str, cols: str, entries: list):
        sql_string = sql_insert_formatter(table, cols, entries)
        placeholder = [value for entry in entries for value in entry]
        cursor.execute(sql_string, tuple(placeholder))
        return {
            'message': 'INSERT SUCCESSFUL'
        }
