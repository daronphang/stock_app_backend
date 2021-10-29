from marshmallow import Schema, fields


class SignUpSchema(Schema):
    firstName = fields.Str()
    lastName = fields.Str()
    email = fields.Str()
    password = fields.Str()


class LoginSchema(Schema):
    email = fields.Str()
    password = fields.Str()


class UserSchema(Schema):
    _id = fields.Str(),
    isOAuth = fields.Number(),
    provider = fields.Str(),
    providerId = fields.Str(),
    requesterAccessToken = fields.Str(),
    requesterRefreshToken = fields.Str(),
    firstName = fields.Str(),
    lastName = fields.Str(),
    email = fields.Str(),
    password = fields.Str(),
    createdAt = fields.DateTime(),
    updatedAt = fields.DateTime()