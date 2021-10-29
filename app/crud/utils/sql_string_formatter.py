# query format:
# {'AND': ['>=', {'id: 1, 'name': 'john'}]}
# default operators are AND and '=' unless specified in query

def query(query: dict):
    # Default query with AND and '=' operators
    operator_set = set(['AND', 'OR'])

    if not bool(set(query.keys()).intersection(operator_set)):
        query_string = ''
        for key in query:
            query_string += 'AND {} = %s'.format(key)
        return query_string[4:], query.values()
    else:
        query_string = ''
        for operator, list in query.items():
            equality = list[0]
            for key in list[1]:
                query_string += '{} {} {} %s '.format(operator, equality, key)
        values = [
            value for item in query.values() for value in item.values()
        ]
        return query_string[len(operator):], values


def sql_query_formatter(table: str, query_dict: dict):
    query_string, values = query(query_dict)
    sql_string = 'SELECT * FROM {} WHERE {}'.format(table, query_string)
    return sql_string, values


def sql_insert_formatter(table: str, cols: str, entries: list):
    # (%s, %s, %s),(%s, %s, %s)
    placeholder_string = ''
    for entry in entries:
        # (%s, %s, %s)
        entry_string = ''
        for i in range(len(entries[0])):
            entry_string += '%s,'
        placeholder_string += '(' + entry_string[:-1] + '),'

    sql_string = 'INSERT INTO {}{} VALUES {}'.format(
        table,
        cols,
        placeholder_string[:-1]
    )
    return sql_string


def sql_update_formatter(table: str, update_fields: dict, query: dict):
    query_string, values = query(query)
    set_string = ''
    for key in update_fields:
        set_string += '{} = %s,'.format(key)

    sql_string = 'UPDATE {} SET {} WHERE {}'.format(
        table,
        set_string[:-1],
        query_string
    )  
    return sql_string, values


def sql_delete_formatter(table: str, query_dict: dict):
    query_string, values = query(query_dict)
    sql_string = 'DELETE * FROM {} WHERE {}'.format(table, query_string)
    return sql_string, values