CREATE DEFINER=`root`@`localhost` PROCEDURE `createPortfolio`(
IN delim VARCHAR(10),
IN portfolio_userId CHAR(36),
IN portfolio_portfolioName VARCHAR(200),
IN portfolio_tickerCount INT,
IN portfolio_orderId INT,
IN tickers_userId_list VARCHAR(1000),
IN tickers_portfolioName_list VARCHAR(1000),
IN tickers_orderId_list VARCHAR(1000),
IN tickers_ticker_list VARCHAR(1000)
)
BEGIN
DECLARE count INT DEFAULT 1;
DECLARE delimiterCount INT;

DECLARE EXIT HANDLER FOR SQLEXCEPTION
	BEGIN
    ROLLBACK;
    RESIGNAL;
END;

START TRANSACTION;
	/*Get delimiter count, number of times to loop*/
	SET delimiterCount = LENGTH(tickers_userId_list) - LENGTH(REPLACE(tickers_userId_list, delim, '')) + 1;

	/*Add to user_portfolio table*/
	INSERT INTO user_portfolios (userId, portfolioName, tickerCount, orderId)
	VALUES (portfolio_userId, portfolio_portfolioName, portfolio_tickerCount, portfolio_orderId);

	/*Add to user_portfolio_tickers table with dynamic number of insert rows*/
	WHILE delimiterCount > 0 DO
		SET @user_id = CONVERT(SPLIT_STR(tickers_userId_list, delim, count), CHAR(36));
		SET @portfolio_name = CONVERT(SPLIT_STR(tickers_portfolioName_list, delim, count), CHAR(200));
		SET @order_id = CONVERT(SPLIT_STR(tickers_orderId_list, delim, count), SIGNED);
		SET @ticker = CONVERT(SPLIT_STR(tickers_ticker_list, delim, count), CHAR(10));
		INSERT INTO user_portfolio_tickers (userId, portfolioName, orderId, ticker)
		VALUES (@user_id, @portfolio_name, @order_id, @ticker);
		SET delimiterCount = delimiterCount - 1;
		SET count = count + 1;
	END WHILE;
COMMIT;
END