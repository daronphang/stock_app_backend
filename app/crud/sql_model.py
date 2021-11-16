import inspect
from functools import wraps
from app.crud.utils.sql_connection import MySQLDBConnectionSession
from app.crud.utils.sql_string_formatter import (
    sql_insert_formatter,
    sql_query_formatter,
    sql_update_formatter,
    sql_delete_formatter
)


# Decorator for sql connection and cursor execution
def sql_connection(is_dict):
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
                        'error': str(e)
                    }
        return wrapper
    return inner_decorator


# QUERY method, allows multiple queries
# Query key/values in dict format
# default operators are AND and '=' unless specified in query
@sql_connection(True)
def sql_find(self, cursor, col: str, table: str, query: dict):
    sql_string, values = sql_query_formatter(col, table, query)
    cursor.execute(sql_string, tuple(values))
    if cursor.with_rows:
        return {
            'results': cursor.fetchall(),
            'row_count': cursor.rowcount,
            'statement': cursor.statement,
        }
    else:
        return {
            'row_count': 0
        }


# UPDATE method
# conditions is a list of dict {
# 'field': 'id', 'equality': '=', 'condition': 1, 'value': 5
# }
@sql_connection(False)
def sql_update(
    self,
    cursor,
    table: str,
    update_field: str,
    conditions: list,
    query: dict
):
    sql_string, values = sql_update_formatter(
        table,
        update_field,
        conditions,
        query
    )

    cursor.execute(sql_string, tuple(values))
    return {
        'row_count': cursor.rowcount,
        'statement': cursor.statement
    }


# DELETE method
@sql_connection(False)
def sql_delete(self, cursor, table: str, query: dict):
    # get initial row count from table
    cursor.execute('SELECT * FROM {}'.format(table))
    cursor.fetchall()
    initial_row_count = cursor.rowcount

    sql_string, values = sql_delete_formatter(table, query)
    cursor.execute(sql_string, tuple(values))
    statement = cursor.statement

    # # get deleted row count
    cursor.execute('SELECT * FROM {}'.format(table))
    cursor.fetchall()
    final_row_count = cursor.rowcount
    deleted_row_count = initial_row_count - final_row_count
    return {
        'statement': statement,
        'deleted_row_count': deleted_row_count
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
    # if cols arg is specified, format is '(col1, col2)'
    @sql_connection(False)
    def sql_insert(self, cursor, table: str, cols: str, entries: list):
        cols = str(inspect.signature(self.__class__)) if not cols else cols
        sql_string, values = sql_insert_formatter(table, cols, entries)
        cursor.execute(sql_string, tuple(values))
        return {
            'row_count': cursor.rowcount,
            'statement': cursor.statement,
            'lastrowid': cursor.lastrowid
        }
