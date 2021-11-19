CREATE DEFINER=`root`@`localhost` FUNCTION `SPLIT_STR`(
list VARCHAR(1000),
delim VARCHAR (10),
pos INT
) RETURNS varchar(255) CHARSET utf8mb4
    DETERMINISTIC
BEGIN
RETURN
 REPLACE(
SUBSTRING_INDEX(list, delim, pos),
CONCAT(SUBSTRING_INDEX(list, delim, pos -1), delim),
''
);
END