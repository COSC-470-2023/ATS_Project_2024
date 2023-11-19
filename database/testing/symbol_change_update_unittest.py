import unittest
import json
import traceback

from database.processing.symbol_change_update import load_output_file, update_symbol, connect


class SymbolChangeTest(unittest.TestCase):
    def createTestDB(self):
        # Connect to the test database
        self.conn = connect.connect()
        # Create a test Companies table
        self.conn.execute("CREATE TABLE `companies` (`id` BIGINT, `companyName` VARCHAR(300) NOT NULL, `symbol` VARCHAR(10) NOT NULL, `isListed` boolean, PRIMARY KEY (`id`))")


    def dropTestDB(self):
        # drop test table
        self.conn.execute("DROP TABLE Companies")
        # Close the connection
        self.conn.close()


    def test_load_output_file(self):
        test1 = load_output_file(r"test1.json")
        test2 = load_output_file(r"test2.json")
        test3 = load_output_file(r"test3.json")

    def test_update_symbol(self):
        test1 = load_output_file(r"test1.json")
        test2 = load_output_file(r"test2.json")
        test3 = load_output_file(r"test3.json")
        test_db()


if __name__ == '__main__':
    unittest.main()

