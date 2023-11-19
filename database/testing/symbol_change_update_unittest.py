import unittest
import json
import traceback
import sys
from sqlalchemy import text

from database.processing import symbol_change_update, connect, credentials
from database.processing.symbol_change_update import load_output_file, update_symbol


class SymbolChangeTest(unittest.TestCase):
    def createTestDB(self):
        # connect to the test database
        self.conn = connect.connect()
        # create a test Companies table
        create = text(f"CREATE TABLE `CompaniesTest` (`id` BIGINT, `companyName` VARCHAR(300) NOT NULL, `symbol` VARCHAR(10) NOT NULL, `isListed` boolean, PRIMARY KEY (`id`))")
        with self.conn as conn:
            conn.execute(create)

    def dropTestDB(self):
        # drop test table
        self.conn.execute("DROP TABLE CompaniesTest")
        # Close the connection
        self.conn.close()

    def test_update_symbol(self):
        self.createTestDB()
        # load test data
        test1 = load_output_file(r"test1.json")
        test2 = load_output_file(r"test2.json")
        test3 = load_output_file(r"test3.json")

        #check to see if the loaded test data is a proper list
        self.assertIsInstance(test1, list)
        self.assertIsInstance(test2, list)
        self.assertIsInstance(test3, list)

        #check if the update_symbol function runs without errors. function should return nothing if no errors occured
        with self.subTest("Test one"):
            self.assertIsNone(update_symbol(self.conn, test1[0]))
        with self.subTest("Test two"):
            self.assertIsNone(update_symbol(self.conn, test2[0]))
        with self.subTest("Test three"):
            self.assertIsNone(update_symbol(self.conn, test3[0]))
        self.dropTestDB()

if __name__ == '__main__':
    unittest.main()

