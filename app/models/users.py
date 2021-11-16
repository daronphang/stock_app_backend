from werkzeug.security import check_password_hash
from app.crud.sql_model import SQLMixin, sql_connection
from app.crud.utils.sql_string_formatter import (
    sql_query_formatter,
    sql_insert_formatter
)


class User(SQLMixin):
    def __init__(
        self,
        _id,
        isOAuth,
        provider,
        providerId,
        requesterAccessToken,
        requesterRefreshToken,
        firstName,
        lastName,
        email,
        password,
    ):
        self._id = _id
        self.isOAuth = isOAuth
        self.provider = provider
        self.providerId = providerId
        self.requesterAccessToken = requesterAccessToken
        self.requesterRefreshToken = requesterRefreshToken
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.password = password

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    @sql_connection(True)
    def signup(self, cursor):
        # Check if user exists in database
        sql_query, query_values = sql_query_formatter(
            '*',
            'users',
            {'email': self.email}
        )
        cursor.execute(sql_query, tuple(query_values))
        if cursor.with_rows:
            user_exists = cursor.fetchall()
            if user_exists:
                return {
                    "message": "USER_EXISTS"
                }
        sql_insert, insert_values = sql_insert_formatter(
            'users',
            self.get_class_attr(),
            self.get_class_attr_values()
        )
        cursor.execute(sql_insert, insert_values)
        return {
            'message': 'CREATE_USER_SUCCESSFUL',
            'statement': cursor.statement
        }
