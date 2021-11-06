from werkzeug.security import check_password_hash
from app.crud.sql_model import SQLMixin


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
