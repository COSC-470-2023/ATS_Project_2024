import unittest
from sqlalchemy import text

import sys
sys.path.insert(0, '../processing')
import connect
import historical_commodity_insert as ht
import realtime_commodity_insert as rt

class CommodityTest(unittest.TestCase):
                    
    def test_historical(self):
        data = ht.load_output_file("../../test_files/static_test_files/static_commodities_historical.json")
        with connect.connect() as conn:
            for entry in data:
                commodity_id = ht.get_commodity_id(entry, conn)
                ht.execute_insert(conn, entry, commodity_id)
            result = conn.execute(text(f"select id from `commodities` where symbol = 'HGUSD'"))
            row = result.one_or_none()
            self.assertIsNotNone(row, msg="The insertion script did not insert into commodities as expected, as the expected row was not found in the database.")
            retrieved_commodity_id = row[0]
            result = conn.execute(text(f"select volume from `historical_commodity_values` where commodity_id = '{retrieved_commodity_id}' and date = '2023-11-23'"))
            row = result.one_or_none()
            self.assertIsNotNone(row, msg="The insertion script did not insert into historical_commodity_values as expected, as the expected row was not found in the database.")
            volume = row[0]
            self.assertEqual(volume, 22865, msg="Volume doesn't match the expected value. Either the test JSON was altered, or the insertion script is inserting the wrong value.")
            
    def test_realtime(self):
        data = rt.load_output_file("../../test_files/static_test_files/static_commodities_realtime.json")
        with connect.connect() as conn:
            for entry in data:
                commodity_id = rt.get_commodity_id(entry, conn)
                rt.execute_insert(conn, entry, commodity_id)
            result = conn.execute(text(f"select id from `commodities` where symbol = 'HGUSD'"))
            row = result.one_or_none()
            self.assertIsNotNone(row, msg="The insertion script did not insert into commodities as expected, as the expected row was not found in the database.")
            retrieved_commodity_id = row[0]
            result = conn.execute(text(f"select volume from `realtime_commodity_values` where commodity_id = '{retrieved_commodity_id}'"))
            row = result.one_or_none()
            self.assertIsNotNone(row, msg="The insertion script did not insert into realtime_commodity_values as expected, as the expected row was not found in the database.")
            volume = row[0]
            self.assertEqual(volume, 13394, msg="Volume doesn't match the expected value. Either the test JSON was altered, or the insertion script is inserting the wrong value.")

    
if __name__ == '__main__':
    unittest.main(verbosity=2)
