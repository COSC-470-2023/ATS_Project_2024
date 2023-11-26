# https://docs.sqlalchemy.org/en/20/changelog/migration_20.html

import traceback
import sys
import os
import connect
import historical_commodities_db_script as ht
import realtime_commodities_db_script as rt
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
    
    """def test_realtime(self):
        code = 0;
        try:
            rt.
            engine = create_engine(uri)
            with self.assertRaises(IntegrityError):
                with engine.connect() as conn:
                    conn.execute(text("insert into `Bonds` values (null, null, null)"))
                    conn.commit()
        except:
            code = 1;
        finally:
            self.assertLessEqual(code, 0)"""
                
    # currently out of commission as historical doesn't work regardless    
    """def test_historical(self):
        code = 0
        try:
            ht.insert("historical_commodity_test.json")
            with connect.connect() as conn:
                result = conn.execute(text(f"select id from `commodities` where symbol = 'HGUSD'"))
                row = result.one_or_none()
                CommodityID = row[0] # attempting to throw an exception
                result = conn.execute(text(f"select id from `historical_commodities_values` where date = '2023-11-16'"))
                row = result.one_or_none()
                CommodityID2 = row[0] # attempting to throw an exception
                if CommodityID != CommodityID2:
                    code = 1
        except:
            code = 1
        finally:
            self.assertLessEqual(code, 0)"""
            
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
                self.assertEqual(volume, 13394, msg="Volume doesn't match 13394. Either the test JSON was altered, or the insertion script is inserting the wrong value.")

    
if __name__ == '__main__':
    unittest.main(verbosity=2)
