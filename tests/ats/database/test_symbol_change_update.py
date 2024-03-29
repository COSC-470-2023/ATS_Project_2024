# Just as a heads up, this unit test doesn't verify if the old symbol is gone or if the new symbol is there
import unittest

from ats.database import symbol_change_update
from ats.util import db_handler


# class SymbolChangeTest(unittest.TestCase):
#
#     def test_empty(self):
#         print("Starting Test 1...")
#
#         # Load test data
#         test1 = symbol_change_update.load_output_file(r"symbol_change_test1.json")
#
#         # Check to see if the loaded test data is a proper list
#         self.assertIsInstance(test1, list)
#
#         # Check if the update_symbol function runs without errors. function should return nothing if no errors occurred
#         with connect.connect() as conn:
#             for symbol in test1:
#                 print("Symbol Changed: ", symbol)
#                 self.assertIsNone(symbol_change_update.update_symbol(conn, test1[0]))
#
#         print("Test 1 Complete")
#
#     def test_one(self):
#         print("Starting Test 2...")
#
#         # Load test data
#         test2 = symbol_change_update.load_output_file(r"symbol_change_test2.json")
#
#         # Check to see if the loaded test data is a proper list
#         self.assertIsInstance(test2, list)
#
#         # Check if the update_symbol function runs without errors. function should return nothing if no errors occurred
#         with connect.connect() as conn:
#             for symbol in test2:
#                 print("Symbol Changed: ", symbol)
#                 self.assertIsNone(symbol_change_update.update_symbol(conn, test2[0]))
#
#         print("Test 2 Complete")
#
#     def test_two(self):
#         print("Starting Test 3...")
#
#         # Load test data
#         test3 = symbol_change_update.load_output_file(r"symbol_change_test3.json")
#
#         # Check to see if the loaded test data is a proper list
#         self.assertIsInstance(test3, list)
#
#         # Check if the update_symbol function runs without errors. function should return nothing if no errors occurred
#         with connect.connect() as conn:
#
#             for symbol in test3:
#                 print("Symbol Changed: ", symbol)
#                 self.assertIsNone(symbol_change_update.update_symbol(conn, test3[0]))
#
#         print("Test 3 Complete")
