import unittest
from database.processing import connect
from database.processing.symbol_change_update import load_output_file, update_symbol

class SymbolChangeTest(unittest.TestCase):
    def test_update_symbol(self):
        try:
            # Load test data
            test1 = load_output_file(r"test1.json")
            test2 = load_output_file(r"test2.json")
            test3 = load_output_file(r"test3.json")

            # Check to see if the loaded test data is a proper list
            self.assertIsInstance(test1, list)
            self.assertIsInstance(test2, list)
            self.assertIsInstance(test3, list)

            # Check if the update_symbol function runs without errors. function should return nothing if no errors occured
            with connect.connect() as conn:
                with self.subTest("Test one"):
                    print("Starting Test 1...")
                    for symbol in test1:
                        print("Symbol Changed: ", symbol)
                        self.assertIsNone(update_symbol(conn, test1[0]))
                    print("Test 1 Complete ✔")
                with self.subTest("Test two"):
                    print("Starting Test 2...")
                    for symbol in test2:
                        print("Symbol Changed: ", symbol)
                        self.assertIsNone(update_symbol(conn, test2[0]))
                    print("Test 2 Complete ✔")
                with self.subTest("Test three"):
                    print("Starting Test 3...")
                    for symbol in test3:
                        print("Symbol Changed: ", symbol)
                        self.assertIsNone(update_symbol(conn, test3[0]))
                    print("Test 3 Complete ✔")

        except Exception as e:
            print(e)


if __name__ == '__main__':
    unittest.main()
