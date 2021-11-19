from flask import g
from app.crud.sql_model import SQLMixin, sql_connection
from app.crud.utils.sql_string_formatter import (
    sql_update_cond_only_formatter
)


class Portfolio(SQLMixin):
    def __init__(
        self,
        user_id,
        portfolio_name,
        order_id,
        tickers,
    ):
        self.user_id = user_id
        self.portfolio_name = portfolio_name
        self.order_id = order_id
        self.tickers = tickers  # ['JPM', 'TESLA', 'APPS']

    @staticmethod
    @sql_connection(True)
    def get_portfolios(self, cursor):
        # Cursor fetches two queries from tables user_portfolios and tickers
        cursor.callproc('getPortfolios', (g.user_payload['sub'],))
        portfolios = [result.fetchall() for result in cursor.stored_results()]

        # Get list of portfolio names and sort by orderId
        # final output is list of strings only ['Fintech', 'Semiconductor']
        raw_portfolio_list = sorted(portfolios[0], key=lambda x: x['orderId'])
        final_portfolio_list = [
            {
                'name': item['portfolioName'],
                'orderId': item['orderId']
            } for item in raw_portfolio_list
            ]

        # Get all tickers and sort tickers by orderId for each portfolio
        # final result is an ordered dict
        # {
        # 'fintech': ['JPM', 'MS'],
        # 'automobile: ['TSLA', 'NIO']
        # }
        raw_tickers = portfolios[1]
        results = []
        for obj in final_portfolio_list:
            # Initially get list of unordered items for a portfolio
            raw_list = [
                item for item in raw_tickers 
                if item['portfolioName'] == obj['name']
            ]
            # insert into ordered_dict with portfolio name and ordered tickers
            raw_list.sort(key=lambda x: x['orderId'])
            final_list = [x['ticker'] for x in raw_list]
            results.append({
                'portfolioName': obj['name'],
                'tickers': final_list,
                'orderId': obj['orderId']
            })

        # When jsonifying, it doesn't respect order & sorts key alphabetically
        # Cannot use OrderedDict()
        return results

    @sql_connection(False)
    def create_portfolio(self, cursor):
        # Add to portfolio and portfolio ticker tables
        order_id_list = list(range(1, len(self.tickers) + 1))
        id_str = '{},'.format(self.user_id) * len(self.tickers)
        name_str = '{},'.format(self.portfolio_name) * len(self.tickers)
        order_id_str = ','.join([str(id) for id in order_id_list])
        ticker_str = ','.join(self.tickers)

        cursor.callproc('createPortfolio', (
            ',',
            self.user_id,
            self.portfolio_name,
            len(self.tickers),
            self.order_id,
            id_str[:-1],
            name_str[:-1],
            order_id_str,
            ticker_str
        ))

        return {
            'message': 'CREATE_PORTFOLIO_SUCCESSFUL',
            'row_count': cursor.rowcount,
            'statement': cursor.statement,
            'lastrowid': cursor.lastrowid
        }

    @sql_connection(False)
    def add_portfolio(self, cursor):
        # Add new tickers and update portfolio ticker count
        order_id_list = [item['orderId'] for item in self.tickers]
        user_id_str = '{},'.format(self.user_id) * len(self.tickers)
        name_str = '{},'.format(self.portfolio_name) * len(self.tickers)
        order_id_str = ','.join([str(id) for id in order_id_list])
        new_ticker_str = ','.join([item['ticker'] for item in self.tickers])

        cursor.callproc('addPortfolio', (
            ',',
            self.user_id,
            self.portfolio_name,
            max(order_id_list),
            user_id_str[:-1],
            name_str[:-1],
            order_id_str,
            new_ticker_str
        ))
        return {
            'message': 'ADD_PORTFOLIO_SUCCESSFUL',
            'statement': cursor.statement
        }

    @staticmethod
    @sql_connection(False)
    def reorder_portfolio(self, cursor, update_data: list):
        order_id_list = [item['orderId'] for item in update_data]
        portfolio_name_str = ','.join(
            [item['portfolioName'] for item in update_data]
        )
        order_id_str = ','.join([str(item) for item in order_id_list])
        cursor.callproc('reorderPortfolio', (
            ',',
            g.user_payload['sub'],
            order_id_str,
            portfolio_name_str
            )
        )
        return {
            'message': 'REORDER_PORTFOLIO_SUCCESSFUL',
            'statement': cursor.statement
        }

    @staticmethod
    @sql_connection(False)
    def update_portfolio(
        self,
        cursor,
        portfolio_name,
        new_portfolio_name,
        del_tickers,
        tickers
    ):
        # User has option to change name/delete tickers/reorder
        del_ticker_str = ','.join(del_tickers)
        order_id_list = list(range(1, len(tickers) + 1))
        order_id_str = ','.join(str(item) for item in order_id_list)
        update_ticker_str = ','.join(tickers)

        cursor.callproc('updatePortfolio', (
            ',',
            g.user_payload['sub'],
            portfolio_name,
            len(tickers),
            new_portfolio_name,
            del_ticker_str,
            order_id_str,
            update_ticker_str
            )
        )
        return {
            'message': 'UPDATE_PORTFOLIO_SUCCESSFUL',
            'row_count': cursor.rowcount,
            'statement': cursor.statement
        }

    @staticmethod
    @sql_connection(True)
    def delete_portfolio(
        self,
        cursor,
        del_portfolio_name: str,
        update_list: list
    ):
        # Deletes portfolio, tickers, and reorders portfolio number
        # If deleted portfolio is last item, don't need to update orderId
        if not update_list:
            cursor.callproc(
                'deletePortfolioNoUpdate',
                (g.user_payload['sub'], del_portfolio_name)
            )
        else:
            conditions = {
                'case_field': 'portfolioName',
                'equality': '=',
                'case_values': [
                    item['portfolioName'] for item in update_list
                ],
                'values': [
                    item['orderId'] for item in update_list
                ]
            }
            sql_case = sql_update_cond_only_formatter('orderId', conditions)
            cursor.callproc('deletePortfolio', (
                g.user_payload['sub'],
                del_portfolio_name,
                sql_case
                )
            )
        return {
            'message': 'DELETE_PORTFOLIO_SUCCESSFUL',
            'row_count': cursor.rowcount,
            'statement': cursor.statement
        }
