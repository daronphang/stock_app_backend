from marshmallow import Schema, fields


class SignUpSchema(Schema):
    firstName = fields.Str()
    lastName = fields.Str()
    email = fields.Str()
    password = fields.Str()
