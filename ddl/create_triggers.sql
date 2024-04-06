/* 
    - This file contains the triggers required for database opertions of the Algorithmic Trading System 
    - Triggers must applied to the database created by ./database/ddl/create_db.sql to ensure the proper functionality of the system.
*/

/* 
----------------------
ID Generation Triggers
----------------------
Handle the creation of unique identifiers for market entities
*/

-- Companies Trigger
DELIMITER $$
CREATE TRIGGER companies_id_gen_trg
BEFORE INSERT ON companies
FOR EACH ROW
BEGIN
    -- vars
	DECLARE new_id BIGINT;
	DECLARE temp INTEGER;
	DECLARE valid INTEGER;
    SET new_id = UUID_SHORT();
    SET valid = 1;
	-- code
	SELECT COUNT(*) INTO temp FROM companies WHERE symbol = NEW.symbol;
	IF (temp = 0) THEN
    	WHILE (valid = 1) DO
        	SELECT COUNT(*) INTO temp FROM companies WHERE id = new_id;
        	IF (temp = 1) THEN
            	SET new_id = UUID_SHORT();
   			  ELSE
   		 		SET valid = 0;
        	END IF;
    	END WHILE;
    ELSE
    	SIGNAL SQLSTATE '45000'
   		SET MESSAGE_TEXT = 'A record for this stock already exists.';
    END IF;
	SET NEW.id = new_id;
END;
$$
DELIMITER ;

-- Commodities Trigger
DELIMITER $$
CREATE TRIGGER commodities_id_gen_trg
BEFORE INSERT ON commodities
FOR EACH ROW
BEGIN
	-- vars
	DECLARE new_id BIGINT;
	DECLARE temp INTEGER;
	DECLARE valid INTEGER;
    SET new_id = UUID_SHORT();
    SET valid = 1;
	-- code
	SELECT COUNT(*) INTO temp FROM commodities WHERE Symbol = NEW.Symbol;
	IF (temp = 0) THEN
    	WHILE (valid = 1) DO
        	SELECT COUNT(*) INTO temp FROM commodities WHERE id = new_id;
        	IF (temp = 1) THEN
            	SET new_id = UUID_SHORT();
   		 	  ELSE
   		 		SET valid = 0;
        	END IF;
    	END WHILE;
    ELSE
    	SIGNAL SQLSTATE '45000'
   	  SET MESSAGE_TEXT = 'A record for this commodity already exists.';
    END IF;
	SET NEW.ID = new_id;
END;
$$
DELIMITER ;

-- Index Trigger
DELIMITER $$
CREATE TRIGGER indexes_id_gen_trg
BEFORE INSERT ON indexes
FOR EACH ROW
BEGIN
	-- vars
	DECLARE new_id BIGINT;
	DECLARE temp INTEGER;
	DECLARE valid INTEGER;
    SET new_id = UUID_SHORT();
    SET valid = 1;
	-- code
	SELECT COUNT(*) INTO temp FROM indexes WHERE symbol = NEW.symbol;
	IF (temp = 0) THEN
    	WHILE (valid = 1) DO
        	SELECT COUNT(*) INTO temp FROM indexes WHERE id = new_id;
        	IF (temp = 1) THEN
            	SET new_id = UUID_SHORT();
   		 	  ELSE
   		 		SET valid = 0;
        	END IF;
    	END WHILE;
    ELSE
    	SIGNAL SQLSTATE '45000'
   	 	SET MESSAGE_TEXT = 'A record for this index already exists.';
    END IF;
	SET NEW.ID = new_id;
END;
$$
DELIMITER ;

-- Bonds Trigger
DELIMITER $$
CREATE TRIGGER bonds_id_gen_trg
BEFORE INSERT ON bonds
FOR EACH ROW
BEGIN
	-- vars
	DECLARE new_id BIGINT;
	DECLARE temp INTEGER;
	DECLARE valid INTEGER;
    SET new_id = UUID_SHORT();
    SET valid = 1;
	-- code
	SELECT COUNT(*) INTO temp FROM bonds WHERE treasuryName = NEW.treasuryName;
	IF (temp = 0) THEN
    	WHILE (valid = 1) DO
        	SELECT COUNT(*) INTO temp FROM bonds WHERE id = new_id;
        	IF (temp = 1) THEN
            	SET new_id = UUID_SHORT();
   		 	  ELSE
   		 		SET valid = 0;
        	END IF;
    	END WHILE;
    ELSE
    	SIGNAL SQLSTATE '45000'
   	  SET MESSAGE_TEXT = 'A record for this treasury already exists.';
    END IF;
	SET NEW.id = new_id;
END;
$$
DELIMITER ;

/* 
----------------------
Symbol Change Trigger
----------------------
Handles the tracking of changes to records in the companies table. 

Logs are created in the company_changelogs  table.
*/
DELIMITER $$
CREATE TRIGGER symbol_update_trg
AFTER UPDATE ON companies
FOR EACH ROW
BEGIN
    -- vars
	DECLARE temp INTEGER;
    DECLARE symbol_changed BOOLEAN DEFAULT 0;
    DECLARE name_changed BOOLEAN DEFAULT 0;
    DECLARE company_id BIGINT;
    DECLARE change_date DATETIME;
    DECLARE new_symbol VARCHAR(10) DEFAULT null;
    DECLARE new_name VARCHAR(100) DEFAULT null;
    
	-- code
    SELECT COUNT(*) INTO temp FROM companies WHERE id = NEW.id;
    
    -- If company exist in db.
    IF (temp > 0) THEN
        SET company_id = NEW.id;
        SET change_date = NOW();
        -- Check for symbol change
        IF (NEW.symbol != OLD.symbol) THEN
            SET symbol_changed = 1;
            SET new_symbol = NEW.symbol;  
        END IF;
        -- Check for company name change
        IF (NEW.companyName != OLD.companyName) THEN
            SET name_changed = 1;
            SET new_name = NEW.companyName;
        END IF;
        -- Create record of changes in changelogs table
        INSERT INTO company_changelogs VALUES (company_id, change_date, OLD.companyName, new_name, name_changed, OLD.symbol, new_symbol, symbol_changed);
    ELSE
    -- Print message if no company record exists.
        SIGNAL SQLSTATE '45000'
   		SET MESSAGE_TEXT = 'No record of that company.';
    END IF;
END;
$$
DELIMITER ;
