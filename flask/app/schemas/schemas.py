from marshmallow import Schema, fields


class SignUpSchema(Schema):
    firstName = fields.Str()
    lastName = fields.Str()
    email = fields.Str()
    password = fields.Str()


class LoginSchema(Schema):
    email = fields.Str()
    password = fields.Str()


class UpdateSchema(Schema):
    portfolioName = fields.Str()
    newPortfolioName = fields.Str()
    delTickers = fields.List(fields.Str())
    tickers = fields.List(fields.Str())


class PortfolioSchema(Schema):
    portfolioName = fields.Str()
    tickers = fields.List(fields.Str())
    orderId = fields.Number()


class AddSchema(Schema):
    portfolioName = fields.Str()
    newTickers = fields.List(fields.Dict())


class DeleteSchema(Schema):
    delPortfolioName = fields.Str()
    updateList = fields.List(fields.Dict())


class ReorderSchema(Schema):
    updateData = fields.List(fields.Dict())