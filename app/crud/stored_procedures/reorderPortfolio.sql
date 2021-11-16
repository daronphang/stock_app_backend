CREATE DEFINER=`root`@`localhost` PROCEDURE `reorderPortfolio`(
IN delim VARCHAR(10),
IN user_id CHAR(36),
IN order_id_list VARCHAR(1000),
IN portfolio_name_list VARCHAR(1000)
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
	SET delimiterCount = LENGTH(order_id_list) - LENGTH(REPLACE(order_id_list, delim, '')) + 1;

	IF EXISTS (SELECT index_name FROM information_schema.statistics WHERE table_name = 'user_portfolios' AND index_name = 'userId_2') THEN
		SET @drop_index = 'ALTER TABLE user_portfolios DROP INDEX userId_2';
		PREPARE dropStmt FROM @drop_index;
		EXECUTE dropStmt;
		DEALLOCATE PREPARE dropStmt;
	END IF;

	/*Update orderId in user_portfolio table*/
	WHILE delimiterCount > 0 DO
		SET @order_id = CONVERT(SPLIT_STR(order_id_list, delim, count), CHAR(200));
		SET @portfolio_name = CONVERT(SPLIT_STR(portfolio_name_list, delim, count), CHAR(200));
		UPDATE user_portfolios SET orderId = @order_id WHERE userId = user_id AND portfolioName = @portfolio_name;
		SET delimiterCount = delimiterCount - 1;
		SET count = count + 1;
	END WHILE;
	ALTER TABLE user_portfolios ADD UNIQUE KEY `userId_2` (`userId`,`orderId`);
COMMIT;
END