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
        # if code is 1, the test failed
        code = 0
        try:
            data = rt.load_output_file("realtime_commodity_test.json")
            with connect.connect() as conn:
                for entry in data: #should just be one
                    commodity_id = rt.get_commodity_id(entry, conn)
                    result = conn.execute(text(f"select id from `commodities` where symbol = 'HGUSD'"))
                    row = result.one_or_none()
                    CommodityID = row[0] # attempting to throw an exception
                    result = conn.execute(text(f"select volume from `realtime_commodity_values` where commodity_id = '{CommodityID}'"))
                    row = result.one_or_none()
                    volume = row[0] # attempting to throw an exception
                    if volume != 13394:
                        # the data inserted was incorrect, or the data retrieved was incorrect
                        code = 1
        except Exception as e:
            # hitting an exception means either lines after 'row =' got a none
            print(e)
            print(traceback.format_exc())
            code = 1
        finally:
            self.assertLessEqual(code, 0)

    
if __name__ == '__main__':
    unittest.main(verbosity=2)
