# query format:
# {'AND': ['>=', {'id: 1, 'name': 'john'}]}
# default operators are AND and '=' unless specified in query

def query(query: dict):
    # Default query with AND and '=' operators
    operator_set = set(['AND', 'OR'])

    if not bool(set(query.keys()).intersection(operator_set)):
        query_string = ''
        for key in query:
            query_string += ' AND {} = %s'.format(key)
        return query_string[5:], query.values()
    else:
        query_string = ''
        for operator, list in query.items():
            equality = list[0]
            for key in list[1]:
                query_string += '{} {} {} %s '.format(operator, key, equality)
        values = [
            value for item in query.values() for value in item.values()
        ]
        return query_string[len(operator):], values


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


def sql_query_formatter(table: str, query_dict: dict):
    query_string, values = query(query_dict)
    sql_string = 'SELECT * FROM {} WHERE {}'.format(table, query_string)
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
    query_string, query_values = query(query_dict)
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
    query_string, query_values = query(query_dict)
    case_string = 'CASE'
    for item in conditions:
        case_string += ' WHEN {}{}%s THEN {}'.format(
            item['field'],
            item['equality'],
            item['value']
        )
    case_string += ' ELSE {} END'.format(update_field)

    sql_string = 'UPDATE {} SET {} = {} WHERE {}'.format(
        table,
        update_field,
        case_string,
        query_string
    )
    condition_values = [item['condition'] for item in conditions]
    values = condition_values + list(query_values)
    return sql_string, values


def sql_delete_formatter(table: str, query_dict: dict):
    query_string, values = query(query_dict)
    sql_string = 'DELETE FROM {} WHERE {}'.format(table, query_string)
    return sql_string, list(values)
