from flask import g, jsonify
from operator import itemgetter
from marshmallow import ValidationError
from app.main import main
from app.models.portfolio import Portfolio
from app.schemas.schemas import (
    PortfolioSchema,
    DeleteSchema,
    ReorderSchema,
    UpdateSchema,
    AddSchema
)
from app.main.errors import (
    bad_request_error,
    validation_error,
)
from app.main.utils.auth import auth_guard


@main.route('/get-portfolios', methods=['GET'])
@auth_guard
def get_portfolios():
    results = Portfolio.get_portfolios(None)
    return jsonify({
        'message': 'GET_PORTFOLIOS_SUCCCESSFUL',
        'results': results
    })


@main.route('/create-portfolio', methods=['POST'])
@auth_guard
def create_portfolio():
    try:
        payload = PortfolioSchema().load(g.request_payload)
    except ValidationError:
        return validation_error('CREATE_PORTFOLIO_SCHEMA_INVALID')

    portfolioName, tickers, orderId = itemgetter(
        'portfolioName',
        'tickers',
        'orderId'
    )(payload)
    new_portfolio = Portfolio(
        g.user_payload['sub'],
        portfolioName,
        orderId, tickers
    )
    rv = new_portfolio.create_portfolio()

    if 'error' in rv:
        return bad_request_error(rv['error'])
    return jsonify(rv)


@main.route('reorder-portfolio', methods=['POST'])
@auth_guard
def reorder_portfolio():
    try:
        payload = ReorderSchema().load(g.request_payload)
    except ValidationError:
        return validation_error('REORDER_PORTFOLIO_SCHEMA_INVALID')
    updateData = itemgetter('updateData')(payload)
    rv = Portfolio.reorder_portfolio(None, updateData)
    return jsonify(rv)


@main.route('add-portfolio', methods=['POST'])
@auth_guard
def add_portfolio():
    try:
        payload = AddSchema().load(g.request_payload)
    except ValidationError:
        return validation_error('ADD_PORTFOLIO_SCHEMA_INVALID')
    portfolioName, newTickers = itemgetter(
        'portfolioName', 'newTickers'
    )(payload)

    new_portfolio = Portfolio(
        g.user_payload['sub'],
        portfolioName,
        None,
        newTickers
    )
    rv = new_portfolio.add_portfolio()
    return jsonify(rv)


@main.route('update-portfolio', methods=['POST'])
@auth_guard
def update_portfolio():
    try:
        payload = UpdateSchema().load(g.request_payload)
    except ValidationError:
        return validation_error('UPDATE_PORTFOLIO_SCHEMA_INVALID')

    portfolioName, newPortfolioName, delTickers, tickers = itemgetter(
        'portfolioName',
        'newPortfolioName',
        'delTickers',
        'tickers',
    )(payload)

    rv = Portfolio.update_portfolio(
        None,
        portfolioName,
        newPortfolioName,
        delTickers,
        tickers
    )

    if 'error' in rv:
        return bad_request_error(rv['error'])
    return jsonify(rv)


@main.route('delete-portfolio', methods=['POST'])
@auth_guard
def delete_portfolio():
    try:
        payload = DeleteSchema().load(g.request_payload)
    except ValidationError:
        return validation_error('DELETE_PORTFOLIO_SCHEMA_INVALID')

    delPortfolioName, updateList = itemgetter(
        'delPortfolioName',
        'updateList'
    )(payload)
    rv = Portfolio.delete_portfolio(
        None,
        delPortfolioName,
        updateList
    )

    if 'error' in rv:
        return bad_request_error(rv['error'])
    return jsonify(rv)
