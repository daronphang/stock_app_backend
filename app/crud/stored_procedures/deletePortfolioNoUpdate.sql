CREATE DEFINER=`root`@`localhost` 
PROCEDURE `deletePortfolioNoUpdate`(IN user_id CHAR(36),IN portfolio_name VARCHAR (255))
BEGIN
DELETE FROM user_portfolios WHERE (userId = user_id AND portfolioName = portfolio_name);
DELETE FROM user_portfolio_tickers WHERE (userId = user_id AND portfolioName = portfolio_name);
END