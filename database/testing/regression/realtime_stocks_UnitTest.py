import connect
import unittest
from realtime_stock_insert import execute_insert, get_company_id, load_output_file, check_keys

realtime_data = load_output_file("database/testing/regression/stocks_test.json")
class StockInsertion(unittest.TestCase):  
    def testCompanyChecker(self):
        with connect.connect() as conn:
            for entry in realtime_data:
                get_company_id(entry, conn)


    def test_check_keys(self):
        # mock entry missing a lot of keys
        entry = {
            "_realtime_date": "2023-01-01",
            "_realtime_price": 100.0,
        }

        # call the function
        keys = check_keys(entry)

        # verify that missing keys are assigned a value of None
        for key, value in keys.items():
            if key not in entry:
                self.assertEqual(value, None)


    def testInsertion(self):
        
        with connect.connect() as conn:
            for entry in realtime_data:
                comp_id = get_company_id(entry, conn)
                execute_insert(conn, entry, comp_id)
        
if __name__ == '__main__':
    unittest.main()