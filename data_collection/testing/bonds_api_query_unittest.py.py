import unittest
import json

import sys
sys.path.insert(0, '../collection')
import bonds_api_query as baq

from sqlalchemy import column, create_engine
from sqlalchemy import select
from sqlalchemy import table
from sqlalchemy import text

from unittest.mock import patch, Mock, MagicMock

class BondsApiQueryTestCase(unittest.TestCase):    
    date_test = baq.create_date_window
    query_test = baq.make_queries

    # Test creating date objects, checking to see if it returns a non-empty list. 
    def test_create_date(self):
        date_list = baq.create_date_window(123)
        self.assertTrue(date_list,"Date list is empty")
    
    # Testing to make queries function 
    # Changes request functionality to mock the API GET request
    @patch('bonds_api_query.requests.get')
    def test_make_queries(self,mock_get):
        # Setting up the mock success condition
        mock_data = json.dumps([{"_bond_name": "US Treasury",
                                        "_bond_date": "2023-11-16",
                                        "_bond_month1": 5.53,
                                        "_bond_month2": 5.55,
                                        "_bond_month3": 5.51,
                                        "_bond_month6": 5.38,
                                        "_bond_year1": 5.23,
                                        "_bond_year2": 4.83,
                                        "_bond_year3": 4.59,
                                        "_bond_year5": 4.43,
                                        "_bond_year7": 4.47,
                                        "_bond_year10": 4.45,
                                        "_bond_year20": 4.82,
                                        "_bond_year30": 4.63
                                        }])

        # Mock the API response
        mock_response = MagicMock()
        mock_response.status_code = 200
#       mock_response.json.return_value = json.loads(mock_data)  # Not used, but better version than the one below 
        mock_response.text = mock_data  # Return mock data as a JSON compatible string
        mock_get.return_value = mock_response

        # Assigning dummy variable data
        api_url = "http://api.com"
        api_key = "api_key"
        api_fields = {'_bond_name': 'Name', '_bond_date': 'date', '_bond_month1': 'one','_bond_month2': 'two', '_bond_month3': 'three', '_bond_month6': 'six','_bond_year1': 'y1','_bond_year2': 'y2','_bond_year3': 'y3','_bond_year5': 'y5','_bond_year7': 'y7','_bond_year10': 'y10','_bond_year20': 'y20','_bond_year30': 'y30'}
        treasuries = [{"name": "Name"}]
        non_api_fields = {"name": {
                                "src": "_config_name",
                                "mapping": "_bond_name",
                                "input_type": "_string",
                                "output_type": "_string"
                            }
                        }
        days_queried = 10

        # Running actual function to test 
        bonds_list = baq.make_queries(api_url, api_key, api_fields, treasuries, non_api_fields, days_queried)
        # Tests 
        self.assertEqual(len(bonds_list),1,"bonds length not equal to 1")
        self.assertEqual(bonds_list[0]['Name'],"US Treasury","Name doesnt match")
        self.assertEqual(bonds_list[0]['y1'],5.23,"Year 1 incorrect")

if __name__ == '__main__':
    unittest.main()
