from flask import g
from app.crud.sql_model import SQLMixin, sql_connection
from app.crud.utils.sql_string_formatter import (
    sql_delete_formatter,
    sql_insert_formatter,
    sql_update_cond_formatter,
    sql_update_formatter
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

    @sql_connection(False)
    def create_portfolio(self, cursor):
        # Add to portfolio table
        portfolio_cols = '(userId, portfolioName, tickerCount, orderId)'
        portfolio_list = [(
            self.user_id,
            self.portfolio_name,
            len(self.tickers),
            self.order_id
        )]
        sql_insert_portfolio, portfolio_values = sql_insert_formatter(
            'user_portfolios',
            portfolio_cols,
            portfolio_list
        )
        cursor.execute(sql_insert_portfolio, tuple(portfolio_values))

        # Add to portfolio_tickers table
        ticker_cols = '(userId, portfolioName, orderId, ticker)'
        ticker_list = []
        for i, ticker in enumerate(self.tickers, 1):
            # format is ('a', 'Fintech', 1, 'SOFI'), ('b', 'Fintech', 2, 'MS')
            temp_tuple = (self.user_id, self.portfolio_name, i, ticker)
            ticker_list.append(temp_tuple)

        sql_insert_tickers, ticker_values = sql_insert_formatter(
            'user_portfolio_tickers',
            ticker_cols,
            ticker_list
        )
        cursor.execute(sql_insert_tickers, tuple(ticker_values))
        return {
            'message': 'CREATE_PORTFOLIO_SUCCESSFUL',
            'row_count': cursor.rowcount,
            'statement': cursor.statement,
            'lastrowid': cursor.lastrowid
        }

    @staticmethod
    @sql_connection(False)
    def update_portfolio(self, cursor, portfolio_name, tickers):
        # User has option to delete tickers, reorder or delete & reorder
        # For simplicity, deletes existing & adds updated portfolio tickers
        query = {
            'userId': g.user_payload['sub'],
            'portfolioName': portfolio_name
        }
        sql_del_tickers, del_ticker_values = sql_delete_formatter(
            'user_portfolio_tickers',
            query
        )
        cursor.execute(sql_del_tickers, tuple(del_ticker_values))

        # After deleting, to add portfolio tickers with updated sort order
        ticker_cols = '(userId, portfolioName, orderId, ticker)'
        ticker_list = []
        for i, ticker in enumerate(tickers, 1):
            temp_tuple = (g.user_payload['sub'], portfolio_name, i, ticker)
            ticker_list.append(temp_tuple)

        sql_insert_tickers, add_ticker_values = sql_insert_formatter(
            'user_portfolio_tickers',
            ticker_cols,
            ticker_list
        )
        cursor.execute(sql_insert_tickers, tuple(add_ticker_values))

        # Update ticker count in user_portfolios
        sql_update_count, update_values = sql_update_formatter(
            'user_portfolios',
            {'tickerCount': len(tickers)},
            query
        )
        cursor.execute(sql_update_count, tuple(update_values))
        return {
            'message': 'UPDATE_PORTFOLIO_SUCCESSFUL',
            'row_count': cursor.rowcount,
            'statement': cursor.statement
        }

    @staticmethod
    @sql_connection(True)
    def delete_portfolio(self, cursor, portfolioName):
        # Stored procedure retrieves portfolios and executes DELETE
        cursor.callproc(
            'deletePortfolio',
            (g.user_payload['sub'], portfolioName)
        )

        # Returns one result set, a list of dict
        portfolios = [result.fetchall() for result in cursor.stored_results()]

        # Only update orderId of portfolios higher than deleted id
        # need retrieve del_id and rows below
        del_id = [
            item['orderId'] for item in portfolios[0]
            if item['portfolioName'] == portfolioName
        ][0]

        update_entries = [
            {
                'field': 'id',
                'equality': '=',
                'condition': item['id'],
                'value': item['orderId'] - 1
            } for item in portfolios[0]
            if item['orderId'] > del_id
        ]

        # If deleted row is last row, don't need to update orderId
        # Updating of entries not in stored_proc due to injection
        # Need to temporarily disable unique constraint and enable after
        if update_entries:
            sql_update_orderId, update_values = sql_update_cond_formatter(
                'user_portfolios',
                'orderId',
                update_entries,
                {'userId': g.user_payload['sub']}
            )
            disable_constraint = 'ALTER TABLE user_portfolios DISABLE KEYS'
            enable_constraint = 'ALTER TABLE user_portfolios ENABLE KEYS'
            cursor.execute(disable_constraint)
            cursor.execute(sql_update_orderId, tuple(update_values))
            cursor.execute(enable_constraint)

        return {
            'message': 'DELETE_PORTFOLIO_SUCCESSFUL',
            'row_count': cursor.rowcount,
            'statement': cursor.statement
        }
