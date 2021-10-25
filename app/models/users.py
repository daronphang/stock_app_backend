from werkzeug.security import generate_password_hash, check_password_hash
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
        createdAt,
        updatedAt
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
        self.password = generate_password_hash(password)
        self.createdAt = createdAt
        self.updatedAt = updatedAt

    def verify_password(self, password):
        return check_password_hash(self.password, password)