from marshmallow import Schema, fields


class SignUpSchema(Schema):
    firstName = fields.Str()
    lastName = fields.Str()
    email = fields.Str()
    password = fields.Str()


class LoginSchema(Schema):
    email = fields.Str()
    password = fields.Str()


class PortfolioSchema(Schema):
    portfolioName = fields.Str()
    tickers = fields.List(fields.Str())
    orderId = fields.Number()


class DeletePortfolioSchema(Schema):
    portfolioName = fields.Str()