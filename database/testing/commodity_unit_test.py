# https://docs.sqlalchemy.org/en/20/changelog/migration_20.html

import traceback
import sys
import os
import connect
import historical_commodity_insert as ht
import realtime_commodity_insert as rt
import unittest

from sqlalchemy import column
from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy import table
from sqlalchemy import text
# common sqlalchemy exceptions
from sqlalchemy.exc import (
    SQLAlchemyError,
    DataError,
    DatabaseError,
    IntegrityError,
    OperationalError,
    ProgrammingError,
    TimeoutError,
)


class CommodityTest(unittest.TestCase):
                    
    def test_historical(self):
        data = ht.load_output_file("historical_commodity_test.json")
        with connect.connect() as conn:
            for entry in data["historicalStockList"]: # should just be one entry, but have to go a layer down anyway
                print(entry)
                commodity_id = ht.get_commodity_id(entry, conn)
                ht.execute_insert(conn, entry, commodity_id)
                result = conn.execute(text(f"select id from `commodities` where symbol = 'HGUSD'"))
                row = result.one_or_none()
                self.assertIsNotNone(row, msg="The insertion script did not insert into commodities as expected, as the expected row was not found in the database.")
                retrieved_commodity_id = row[0]
                self.assertEqual(retrieved_commodity_id, commodity_id, msg="ID doesn't match. get_commodity_id is retrieving the wrong ID.")
                result = conn.execute(text(f"select volume from `historical_commodity_values` where commodity_id = '{commodity_id}'"))
                row = result.one_or_none()
                self.assertIsNotNone(row, msg="The insertion script did not insert into historical_commodity_values as expected, as the expected row was not found in the database.")
                volume = row[0]
                self.assertEqual(volume, 89522, msg="Volume doesn't match the expected value. Either the test JSON was altered, or the insertion script is inserting the wrong value.")
            
    def test_realtime(self):
        data = rt.load_output_file("realtime_commodity_test.json")
        with connect.connect() as conn:
            for entry in data: # should just be one entry, but have to go a layer down anyway
                commodity_id = rt.get_commodity_id(entry, conn)
                rt.execute_insert(conn, entry, commodity_id)
                result = conn.execute(text(f"select id from `commodities` where symbol = 'HGUSD'"))
                row = result.one_or_none()
                self.assertIsNotNone(row, msg="The insertion script did not insert into commodities as expected, as the expected row was not found in the database.")
                retrieved_commodity_id = row[0]
                self.assertEqual(retrieved_commodity_id, commodity_id, msg="ID doesn't match. get_commodity_id is retrieving the wrong ID.")
                result = conn.execute(text(f"select volume from `realtime_commodity_values` where commodity_id = '{commodity_id}'"))
                row = result.one_or_none()
                self.assertIsNotNone(row, msg="The insertion script did not insert into realtime_commodity_values as expected, as the expected row was not found in the database.")
                volume = row[0]
                self.assertEqual(volume, 13394, msg="Volume doesn't match the expected value. Either the test JSON was altered, or the insertion script is inserting the wrong value.")

    
if __name__ == '__main__':
    unittest.main(verbosity=2)
