# String formatters to return sql strings with placeholders

# query format:
# SELECT * FROM table WHERE id=1 OR (id=2 AND name='hello')
# {'>=': {'id': 1}, '=': {'name': 'john'}}
# {'IN': {'color': ['red', 'blue']}}
# {'BETWEEN': {'id': [1, 5]}}
# {
#   'AND': {'=': {'id: 1, 'name': 'john'}}
#   'OR': {'=': {'id: 1, 'name': 'john'}}
# }
# default operators are AND and '=' unless specified in query
def equality_formatter(equality: str, dict: dict):
    equality_string = ''
    placeholder_values = []
    for key, value in dict.items():
        if equality == 'IN':
            placeholder = '(' + '%s,' * len(value)
            placeholder = placeholder[:-1] + ')'
            equality_string += ' AND {} IN {}'.format(key, placeholder)
            placeholder_values += value
            break

        if equality == 'BETWEEN':
            equality_string += ' AND {} BETWEEN {} AND {}'.format(
                key, value[0], value[1]
            )
            placeholder_values += value
            break

        # For <, >, <>, <=, => equalities
        equality_string += ' AND {} {} %s'.format(key, equality)
        placeholder_values.append(value)
    return equality_string, placeholder_values


def sub_query_formatter(query: dict):
    operator_list = ['AND', 'OR']
    operator_equality = [
        'AND', 'OR', '=', '>=', '<>', '<=', '>', '<', 'IN', 'BETWEEN'
    ]

    query_string = ''
    placeholder_values = []
    for key in query:
        # Default query with AND and '=' operators
        if key not in operator_equality:
            query_string += ' AND {} = %s'.format(key)
            placeholder_values.append(query[key])
            continue

        # If user specifies equalities only
        if key not in operator_list:
            equality_string, values = equality_formatter(key, query[key])
            query_string += equality_string
            placeholder_values += values
            continue

        # If user specifies OR/AND operator
        if key in operator_list:
            count = 0
            query_string += ' {} ('.format(key)
            for equality, nested_dict in query[key].items():
                equality_string, values = equality_formatter(
                    equality,
                    nested_dict
                )
                if count == 0:
                    query_string += equality_string[5:]
                else:
                    query_string += equality_string
                placeholder_values += values
                count += 1
            query_string += ')'
            continue

    return query_string[5:], placeholder_values


# dict = {
#     'AND': {'=': {'id': 1, 'name': 'john'}, '>=': {'id': 5}},
#     'OR': {'=': {'id': 1, 'name': 'john'}}
#  }

# dict = {
#     '>=': {'id': 1},
#     '=': {'name': 'john'},
#     'AND': {'=': {'id': 1, 'name': 'john'}, '>=': {'id': 5}},
#     'OR': {'=': {'id': 1, 'name': 'john'}}
# }

# dict = {
#     'userId': 1,
#     'portfolioName': ' hello'
# }
# string, values = sub_query_formatter(dict)
# print(string)
# print(values)


def query_no_placeholder(query: dict):
    operator_set = set(['AND', 'OR'])
    # Default query with AND and '=' operators
    if not bool(set(query.keys()).intersection(operator_set)):
        query_string = ''
        for key, value in query.items():
            query_string += ' AND {} = {}'.format(
                key,
                value if not isinstance(value, str) else "'" + value + "'"
            )
        return query_string[5:]
    else:
        query_string = ''
        for operator, list in query.items():
            equality = list[0]
            for key, value in list[1].items():
                query_string += '{} {} {} {} '.format(
                    operator,
                    key,
                    equality,
                    value
                )
        return query_string[len(operator):]


def sql_query_formatter(col: str, table: str, query_dict: dict):
    query_string, values = sub_query_formatter(query_dict)
    sql_string = 'SELECT {} FROM {} WHERE {}'.format(col, table, query_string)
    return sql_string, values


# entries is a list of tuples
def sql_insert_formatter(table: str, cols: str, entries: list):
    # (%s, %s, %s),(%s, %s, %s)
    placeholder_string = ''
    for entry in entries:
        # (%s, %s, %s)
        entry_string = len(entries[0]) * '%s,'
        placeholder_string += '(' + entry_string[:-1] + '),'

    values = [value for entry in entries for value in entry]
    sql_string = 'INSERT INTO {}{} VALUES {}'.format(
        table,
        cols,
        placeholder_string[:-1]
    )
    return sql_string, values


# For simple updating of rows; allows multiple columns to be updated
def sql_update_formatter(table: str, set_fields: dict, query_dict: dict):
    query_string, query_values = sub_query_formatter(query_dict)
    values = []
    set_string = 'SET '
    for key, value in set_fields.items():
        set_string += '{}=%s,'.format(key)
        values.append(value)
    sql_string = 'UPDATE {} {} WHERE {}'.format(
        table,
        set_string[:-1],
        query_string
    )
    values += query_values
    return sql_string, values


# For updating rows based on conditions
# UPDATE table
# SET col1 =
# CASE
#   WHEN id=1 THEN 'value'
#   WHEN id=2 THEN 'value2'
#   ELSE config_value
# END
# WHERE config_name IN('name1', 'name2')
# conditions is a list of dict {
# 'field': 'id', 'equality': '=', 'condition': 1, 'value': 5
# }
def sql_update_cond_formatter(
    table: str,
    update_field: str,
    conditions: dict,
    query_dict: dict
):
    query_string, query_values = sub_query_formatter(query_dict)
    case_string = 'CASE'
    for item in conditions['values']:
        case_string += ' WHEN {}{}%s THEN {}'.format(
            conditions['case_field'],
            conditions['equality'],
            item
        )
    case_string += ' ELSE {} END'.format(update_field)

    sql_string = 'UPDATE {} SET {} = {} WHERE {}'.format(
        table,
        update_field,
        case_string,
        query_string
    )
    case_values = [item for item in conditions['case_values']]
    values = case_values + list(query_values)
    return sql_string, values


def sql_update_cond_only_formatter(update_field: str, conditions: dict):
    case_string = 'CASE'
    for i, item in enumerate(conditions['values']):
        case_string += ' WHEN {}{}{} THEN {}'.format(
            conditions['case_field'],
            conditions['equality'],
            "'" + conditions['case_values'][i] + "'",
            item
        )
    case_string += ' ELSE {} END'.format(update_field)
    return case_string


def sql_delete_formatter(table: str, query_dict: dict):
    query_string, values = sub_query_formatter(query_dict)
    sql_string = 'DELETE FROM {} WHERE {}'.format(table, query_string)
    return sql_string, list(values)
