# Needs to be updated to test all functionality. Methods should be imported and called in test methods.

import unittest
from sqlalchemy import text

import sys
sys.path.insert(0, '../../database/processing')
import connect
import historical_index_insert as ht
import realtime_index_insert as rt

class IndexTest(unittest.TestCase):

    def test_historical(self):
        data = ht.load_output_file("../../test_files/static_test_files/static_index_historical.json")
        with connect.connect() as conn:
            for entry in data:
                index_id = ht.get_index_id(entry, conn)
                ht.execute_insert(conn, entry, index_id)
            result = conn.execute(text(f"select id from `indexes` where symbol = '^GSPC'"))
            row = result.one_or_none()
            self.assertIsNotNone(row, msg="The insertion script did not insert into indexes as expected, as the expected row was not found in the database.")
            retrieved_index_id = row[0]
            result = conn.execute(text(f"select volume from `historical_index_values` where index_id = '{retrieved_index_id}' and date = '2023-11-22'"))
            row = result.one_or_none()
            self.assertIsNotNone(row, msg="The insertion script did not insert into historical_index_values as expected, as the expected row was not found in the database.")
            volume = row[0]
            self.assertEqual(volume, 3042810000, msg="Volume doesn't match the expected value. Either the test JSON was altered, or the insertion script is inserting the wrong value.")
            
    def test_realtime(self):
        data = rt.load_output_file("../../test_files/static_test_files/static_index_realtime.json")
        with connect.connect() as conn:
            for entry in data:
                index_id = rt.get_index_id(entry, conn)
                rt.execute_insert(conn, entry, index_id)
            result = conn.execute(text(f"select id from `indexes` where symbol = '^GSPC'"))
            row = result.one_or_none()
            self.assertIsNotNone(row, msg="The insertion script did not insert into indexes as expected, as the expected row was not found in the database.")
            retrieved_index_id = row[0]
            result = conn.execute(text(f"select volume from `realtime_index_values` where index_id = '{retrieved_index_id}'"))
            row = result.one_or_none()
            self.assertIsNotNone(row, msg="The insertion script did not insert into realtime_index_values as expected, as the expected row was not found in the database.")
            volume = row[0]
            self.assertEqual(volume, 2502113000, msg="Volume doesn't match the expected value. Either the test JSON was altered, or the insertion script is inserting the wrong value.")

if __name__ == '__main__':
    unittest.main(verbosity=2)