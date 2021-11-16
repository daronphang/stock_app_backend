CREATE DEFINER=`root`@`localhost` PROCEDURE `updatePortfolio`(
IN delim VARCHAR(10),
IN user_id CHAR(36),
IN portfolio_name VARCHAR(200),
IN ticker_count INT,
IN new_portfolio_name VARCHAR(200),
IN del_ticker_list VARCHAR(255),
IN order_id_list VARCHAR(255),
IN update_ticker_list VARCHAR(1000)
)
BEGIN
DECLARE delCount INT DEFAULT 1;
DECLARE orderCount INT DEFAULT 1;
DECLARE delDelimCount INT;
DECLARE orderDelimCount INT;

DECLARE EXIT HANDLER FOR SQLEXCEPTION
	BEGIN
    ROLLBACK;
    RESIGNAL;
END;

IF EXISTS (SELECT index_name FROM information_schema.statistics WHERE table_name = 'user_portfolio_tickers' AND index_name = 'userId_2') THEN
SET @drop_index = 'ALTER TABLE user_portfolio_tickers DROP INDEX userId_2';
PREPARE dropStmt FROM @drop_index;
EXECUTE dropStmt;
DEALLOCATE PREPARE dropStmt;
END IF;

START TRANSACTION;
/*Get delimiter count, number of times to loop*/
SET delDelimCount = LENGTH(del_ticker_list) - LENGTH(REPLACE(del_ticker_list, delim, '')) + 1;
SET orderDelimCount = LENGTH(order_id_list) - LENGTH(REPLACE(order_id_list, delim, '')) + 1;

/*Create temp table of delete tickers to use for IN clause*/
CREATE TEMPORARY TABLE del_ticker_tbl (ticker VARCHAR(10) PRIMARY KEY);
WHILE delDelimCount > 0 DO
SET @del_ticker = CONVERT(SPLIT_STR(del_ticker_list, delim, delCount), CHAR(10));
INSERT INTO del_ticker_tbl (ticker) VALUES (@del_ticker);
SET delDelimCount = delDelimCount - 1;
SET delCount = delCount + 1;
END WHILE;
DELETE FROM user_portfolio_tickers WHERE userId = user_id AND portfolioName = portfolio_name AND ticker IN (SELECT * FROM del_ticker_tbl);

/*Update orderId for remaining tickers in portfolio*/
WHILE orderDelimCount > 0 DO
SET @order_id = CONVERT(SPLIT_STR(order_id_list, delim, orderCount), SIGNED);
SET @update_ticker = CONVERT(SPLIT_STR(update_ticker_list, delim, orderCount), CHAR(10));
UPDATE user_portfolio_tickers SET orderId = @order_id WHERE userId = user_id AND portfolioName = portfolio_name AND ticker = @update_ticker;
SET orderDelimCount = orderDelimCount - 1;
SET orderCount = orderCount + 1;
END WHILE;

/*Update ticker count in user_portfolio*/
UPDATE user_portfolios SET tickerCount = ticker_count WHERE userId = user_id AND portfolioName = portfolio_name;

/*Update to new portfolio name in both user_portfolio and user_portfolio_tickers if true*/
/*Placed at end of procedure as all updates are based on existing portfolio name */
IF NULLIF(new_portfolio_name, '') IS NOT NULL THEN
UPDATE user_portfolios SET portfolioName = new_portfolio_name WHERE userId = user_id AND portfolioName = portfolio_name;
UPDATE user_portfolio_tickers SET portfolioName = new_portfolio_name WHERE userId = user_id AND portfolioName = portfolio_name;
END IF;

ALTER TABLE user_portfolio_tickers ADD UNIQUE KEY `userId_2` (`portfolioName`,`orderId`);
COMMIT;
END