import unittest

import sys
sys.path.insert(0, '../processing')
import connect
from realtime_stock_insert import execute_insert, get_company_id, load_output_file

realtime_data = load_output_file("../../test_files/static_test_files/static_stocks_realtime.json")
class StockInsertion(unittest.TestCase):  
    def testCompanyChecker(self):
        with connect.connect() as conn:
            for entry in realtime_data:
                get_company_id(entry, conn)


    def testInsertion(self):
        
        with connect.connect() as conn:
            for entry in realtime_data:
                comp_id = get_company_id(entry, conn)
                execute_insert(conn, entry, comp_id)
        
if __name__ == '__main__':
    unittest.main()