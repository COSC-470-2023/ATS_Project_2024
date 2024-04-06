import decimal
import unittest

import sqlalchemy

from ats.database import bonds_insert
from ats.util import db_handler


# class BondTest(unittest.TestCase):
#     def test_bond_insertion(self):
#         data = bonds_insert.load_output_file("../../test_files/static_test_files/static_bonds_30day.json")
#         with connect.connect() as conn:
#             for entry in data:
#                 bond_id = bonds_insert.get_bond_id(entry, conn)
#                 bonds_insert.execute_insert(conn, entry, bond_id)
#
#             result = conn.execute(sqlalchemy.text(f"select bond_id from `bonds` where treasuryName = 'US Treasury'"))
#             row = result.one_or_none()
#             self.assertIsNotNone(row, msg="The insertion script did not insert into commodities as expected, as the expected row was not found in the database.")
#             retrieved_bond_id = row[0]
#             result = conn.execute(sqlalchemy.text(f"select 1_year from `bond_values` where bond_id = '{retrieved_bond_id}' and date = '2023-11-14'"))
#             row = result.one_or_none()
#             self.assertIsNotNone(row, msg="The insertion script did not insert into bond_values as expected, as the expected row was not found in the database.")
#             one_year = row[0]
#             self.assertEqual(one_year, decimal.Decimal('5.24'), msg="1_year doesn't match the expected value. Either the test JSON was altered, or the insertion script is inserting the wrong value.")
