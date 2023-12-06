# https://docs.sqlalchemy.org/en/20/changelog/migration_20.html
import connect
import bonds_insert as bd
import unittest
from decimal import *
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


class bondTest(unittest.TestCase):
                    
    def test_bond_insertion(self):
        data = bd.load_output_file("../../test_files/static_test_files/static_bonds_30day.json")
        with connect.connect() as conn:
            for entry in data: 
                bond_id = bd.get_bond_id(entry, conn)
                bd.execute_insert(conn, entry, bond_id)
                
            result = conn.execute(text(f"select bond_id from `bonds` where treasuryName = 'US Treasury'"))
            row = result.one_or_none()
            self.assertIsNotNone(row, msg="The insertion script did not insert into commodities as expected, as the expected row was not found in the database.")
            retrieved_bond_id = row[0]
            self.assertEqual(retrieved_bond_id, bond_id, msg="ID doesn't match. get_bond_id is retrieving the wrong ID.")
            result = conn.execute(text(f"select 1_year from `bonds_values` where bond_id = '{bond_id}' and date = '2023-11-27'"))
            row = result.one_or_none()
            self.assertIsNotNone(row, msg="The insertion script did not insert into bond_values as expected, as the expected row was not found in the database.")
            one_year = row[0]
            self.assertEqual(one_year, Decimal('5.24'), msg="1_year doesn't match the expected value. Either the test JSON was altered, or the insertion script is inserting the wrong value.")

    
if __name__ == '__main__':
    unittest.main(verbosity=2)
