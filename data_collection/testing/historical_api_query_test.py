#import unittest
import pytest
from unittest.mock import Mock
import requests
import time

import sys
sys.path.insert(0, '../collection')
import historical_api_query

#class TestHistoricalApiQueryMethods(unittest.TestCase):
def test_make_queries(self):
    test_url = ('https://www.test.com/api?key={API_KEY}'
                '&query={QUERY_PARAMS}&start={START_DATE}&end={END_DATE}')
    test_key = 'key'
    test_queries = [{
        'symbol': 'AAPL', 
        'start_date': '1976-04-01', 
        'end_date': '2024-01-31'
    }]
    expected_query = ('https://www.test.com/api?key=key&query=AAPL'
                      '&start=1976-04-01&end=2024-01-31')
    
    class MockResponse:
        def json(self):
            return {'historical': [{'test_field': True}]}
    requests.get = Mock(return_value = MockResponse())
    time.sleep = Mock()
    
    output = historical_api_query.make_queries(test_url, test_key, 
                                               test_queries, None, {}, {})
    requests.get.assert_called_with(expected_query)
    self.assertTrue(output[0]['test_field'])

def test_remap_entries(self):
    test_response_data = {
        'historical': [{
            'test_field_entry': True, 'test_field_mapping': None, 
            'test_field_empty': None
        }], 
        'test_field_response': True
    }
    test_query_item = {'name': True}
    test_api_fields = {
        'test_field_entry': 'test_field_entry_new', 
        'test_field_response': 'test_field_response_new', 
        'test_field_empty': None
    }
    test_non_api_fields = {
        'test_field': {
            'src': '_config_name', 'mapping': 'test_field_mapping', 
            'input_type': '_string', 'output_type': '_string'
        }
    }
    expected_output = {
        'test_field_mapping': True, 'test_field_entry_new': True, 
        'test_field_response_new': True
    }
    
    output = historical_api_query.remap_entries(test_response_data, 
                                                test_query_item, 
                                                test_api_fields, 
                                                test_non_api_fields)
    self.assertEqual(3, len(output))
    self.assertTrue(output['test_field_mapping'])
    self.assertTrue(output['test_field_entry_new'])
    self.assertTrue(output['test_field_response_new'])

#if __name__ == '__main__':
#    unittest.main()
