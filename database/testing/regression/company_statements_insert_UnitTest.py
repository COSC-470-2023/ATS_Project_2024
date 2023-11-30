import connect
import unittest
from company_statements_insert import execute_insert, get_company_id, check_keys

company_data = 	[{
	"_company_symbol": "AAPL",
	"_company_date" : "2023-11-17 13:00:01", 
	"_company_price": 178.72,
	"_company_beta": 1.286802,
	"_company_volAvg": 58405568,
	"_company_mktCap": 2794144143933,
	"_company_lastDiv": 0.96,
	"_company_changes": -0.13,
	"_company_name": "Apple Inc.",
	"_company_currency": "USD",
	"_company_cik": "0000320193",
	"_company_isin": "US0378331005",
	"_company_cusip": "037833100",
	"_company_exchangeFullName": "NASDAQ Global Select",
	"_company_exchange": "NASDAQ",
	"_company_industry": "Consumer Electronics",
	"_company_ceo": "Mr. Timothy D. Cook",
	"_company_sector": "Technology",
	"_company_country": "US",
	"_company_fullTimeEmployees": "164000",
	"_company_phone": "408 996 1010",
	"_company_address": "One Apple Park Way",
	"_company_city": "Cupertino",
	"_company_state": "CA",
	"_company_zip": "95014",
	"_company_dcfDiff": 4.15176,
	"_company_dcf": 150.082,
	"_company_ipoDate": "1980-12-12",
	"_company_isEtf": 0,
	"_company_isActivelyTrading": 1,
	"_company_isAdr": 0,
	"_company_isFund": 0
	}]

class StockInsertion(unittest.TestCase):  
    
    def testCompanyChecker(self):
        with connect.connect() as conn:
            for entry in company_data:
                get_company_id(entry, conn)


    def test_check_keys(self):
        # mock entry missing a lot of keys
        entry = {
            "_company_date": "2023-01-01",
            "_company_price": 100.0,
        }

        # call the function
        keys = check_keys(entry)

        # verify that missing keys are assigned a value of None
        for key, value in keys.items():
            if key not in entry:
                self.assertEqual(value, None)


    def testInsertion(self):
        
        with connect.connect() as conn:
            for entry in company_data:
                comp_id = get_company_id(entry, conn)
                execute_insert(conn, entry, comp_id)
        
if __name__ == '__main__':
    unittest.main()