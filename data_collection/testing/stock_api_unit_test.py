import os
from stock_api_unittest import write_files
import unittest
import shutil
import json

class StockApiUnitTest(unittest.TestCase):
    #def setUp(self):
        #self.test_dir = 'stock_unit_test'
        #os.makedirs(self.test_dir, exist_ok = True)
        
       
    def test_unittest(self):
        data = {}
        data["test"] = True
        write_files(data, data, data) #, self.test_dir
        with open('data_collection\output\\raw_stocks_output.json', 'r') as outfile :
            jsonData = outfile.read()
            self.assertEqual(jsonData, '{\n  "test": true\n}', 'Test passed')
        with open('data_collection\output\\raw_index_output.json', 'r') as outfile :
            jsonData = outfile.read()
            self.assertEqual(jsonData, '{\n  "test": true\n}', 'Test passed')
        with open('data_collection\output\\raw_commodity_output.json', 'r') as outfile :
            jsonData = outfile.read()
            self.assertEqual(jsonData, '{\n  "test": true\n}', 'Test passed')
    #def tearDown(self):
    #    shutil.rmtree(self.test_dir)

if __name__ == "__main__":
    unittest.main()
