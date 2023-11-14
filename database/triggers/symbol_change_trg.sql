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
        INSERT INTO company_changelogs VALUES (company_id, change_date, OLD.companyName, new_name, name_changed, 
                                                OLD.symbol, new_symbol, symbol_changed);
    ELSE
    -- Print message if no company record exists.
        SIGNAL SQLSTATE '45000'
   		SET MESSAGE_TEXT = 'No record of that company.';
    END IF;
END;
$$
DELIMITER ;