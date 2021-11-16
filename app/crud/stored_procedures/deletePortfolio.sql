CREATE DEFINER=`root`@`localhost` PROCEDURE `deletePortfolio`(
IN user_id CHAR(36),
IN portfolio_name VARCHAR (255),
IN case_string VARCHAR(1000)
)
BEGIN
SET @updateStmt = CONCAT('UPDATE user_portfolios SET orderId = ', case_string, ' WHERE userId = ?');
SET @a = user_id;
PREPARE updateStmt FROM @updateStmt;

IF EXISTS (SELECT index_name FROM information_schema.statistics WHERE table_name = 'user_portfolios' AND index_name = 'userId_2') THEN
SET @drop_index = 'ALTER TABLE user_portfolios DROP INDEX userId_2';
PREPARE dropStmt FROM @drop_index;
EXECUTE dropStmt;
DEALLOCATE PREPARE dropStmt;
END IF;

DELETE FROM user_portfolios WHERE (userId = user_id AND portfolioName = portfolio_name);
DELETE FROM user_portfolio_tickers WHERE (userId = user_id AND portfolioName = portfolio_name);
EXECUTE updateStmt USING @a;
ALTER TABLE user_portfolios ADD UNIQUE KEY `userId_2` (`userId`,`orderId`);
DEALLOCATE PREPARE updateStmt;
END