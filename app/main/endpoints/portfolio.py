from flask import g, jsonify
from operator import itemgetter
from marshmallow import ValidationError
from app.main import main
from app.models.portfolio import Portfolio
from app.schemas.schemas import PortfolioSchema, DeletePortfolioSchema
from app.main.errors import (
    bad_request_error,
    validation_error,
)
from app.main.utils.auth import auth_guard
from app.crud.sql_model import sql_find


@main.route('/get-portfolios', methods=['GET'])
@auth_guard
def get_portfolios():
    # Get list of portfolio names and sort by orderId
    # final output is list of strings only ['Fintech', 'Semiconductor']
    rv1 = sql_find(None, 'user_portfolios', {'userId': g.user_payload['sub']})
    if 'error' in rv1:
        return bad_request_error(rv1['error'])
    raw_portfolio_list = sorted(rv1['results'], key=lambda x: x['orderId'])
    final_portfolio_list = [
        item['portfolioName'] for item in raw_portfolio_list
        ]

    # Get all tickers and sort tickers by orderId for each portfolio
    # final result is an ordered dict
    # {
    # 'fintech': ['JPM', 'MS'],
    # 'automobile: ['TSLA', 'NIO']
    # }
    rv2 = sql_find(
        None,
        'user_portfolio_tickers',
        {'userId': g.user_payload['sub']}
    )
    raw_tickers_list = rv2['results']
    results = []
    for name in final_portfolio_list:
        # Initially get list of unordered items for a portfolio
        raw_list = [
            item for item in raw_tickers_list if item['portfolioName'] == name
        ]
        # insert into ordered_dict with portfolio name and ordered tickers list
        raw_list.sort(key=lambda x: x['orderId'])
        final_list = [x['ticker'] for x in raw_list]
        results.append({
            'portfolioName': name,
            'tickers': final_list
        })

    # When jsonifying, it doesn't respect order & sorts key alphabetically
    # Cannot use OrderedDict()
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


@main.route('update-portfolio', methods=['POST'])
@auth_guard
def update_portfolio():
    try:
        payload = PortfolioSchema().load(g.request_payload)
    except ValidationError:
        return validation_error('CREATE_PORTFOLIO_SCHEMA_INVALID')

    portfolioName, tickers = itemgetter(
        'portfolioName',
        'tickers',
    )(payload)

    rv = Portfolio.update_portfolio(None, portfolioName, tickers)

    if 'error' in rv:
        return bad_request_error(rv['error'])
    return jsonify(rv)


@main.route('delete-portfolio', methods=['POST'])
@auth_guard
def delete_portfolio():
    try:
        payload = DeletePortfolioSchema().load(g.request_payload)
    except ValidationError:
        return validation_error('DELETE_PORTFOLIO_SCHEMA_INVALID')

    portfolioName = itemgetter('portfolioName')(payload)
    rv = Portfolio.delete_portfolio(None, portfolioName)

    if 'error' in rv:
        return bad_request_error(rv['error'])
    return jsonify(rv)
