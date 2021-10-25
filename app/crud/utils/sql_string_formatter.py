def sql_query_formatter(table: str, query: dict):
    placeholder_string = ''
    # Format: id=%s AND name=%s
    for key in query.keys():
        placeholder_string += '{}=%s AND '.format(key)

    sql_string = 'SELECT * FROM {} WHERE {}'.format(
        table,
        placeholder_string[:-5]
    )
    return sql_string


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
