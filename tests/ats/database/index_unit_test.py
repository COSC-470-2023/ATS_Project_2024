# Needs to be updated to test all functionality. Methods should be imported and called in test methods.

import unittest

import sqlalchemy

from ats.database import historical_index_insert
from ats.database import realtime_index_insert
from ats.util import db_handler


# class IndexTest(unittest.TestCase):
#
#     def test_historical(self):
#         data = historical_index_insert.load_output_file("../../test_files/static_test_files/static_index_historical.json")
#         with connect.connect() as conn:
#             for entry in data:
#                 index_id = historical_index_insert.get_index_id(entry, conn)
#                 historical_index_insert.execute_insert(conn, entry, index_id)
#             result = conn.execute(sqlalchemy.text(f"select id from `indexes` where symbol = '^GSPC'"))
#             row = result.one_or_none()
#             self.assertIsNotNone(row, msg="The insertion script did not insert into indexes as expected, as the expected row was not found in the database.")
#             retrieved_index_id = row[0]
#             result = conn.execute(sqlalchemy.text(f"select volume from `historical_index_values` where index_id = '{retrieved_index_id}' and date = '2023-11-22'"))
#             row = result.one_or_none()
#             self.assertIsNotNone(row, msg="The insertion script did not insert into historical_index_values as expected, as the expected row was not found in the database.")
#             volume = row[0]
#             self.assertEqual(volume, 3042810000, msg="Volume doesn't match the expected value. Either the test JSON was altered, or the insertion script is inserting the wrong value.")
#
#     def test_realtime(self):
#         data = realtime_index_insert.load_output_file("../../test_files/static_test_files/static_index_realtime.json")
#         with connect.connect() as conn:
#             for entry in data:
#                 index_id = realtime_index_insert.get_index_id(entry, conn)
#                 realtime_index_insert.execute_insert(conn, entry, index_id)
#             result = conn.execute(sqlalchemy.text(f"select id from `indexes` where symbol = '^GSPC'"))
#             row = result.one_or_none()
#             self.assertIsNotNone(row, msg="The insertion script did not insert into indexes as expected, as the expected row was not found in the database.")
#             retrieved_index_id = row[0]
#             result = conn.execute(sqlalchemy.text(f"select volume from `realtime_index_values` where index_id = '{retrieved_index_id}'"))
#             row = result.one_or_none()
#             self.assertIsNotNone(row, msg="The insertion script did not insert into realtime_index_values as expected, as the expected row was not found in the database.")
#             volume = row[0]
#             self.assertEqual(volume, 2502113000, msg="Volume doesn't match the expected value. Either the test JSON was altered, or the insertion script is inserting the wrong value.")
