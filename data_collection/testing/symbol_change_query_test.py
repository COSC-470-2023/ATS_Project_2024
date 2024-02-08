import requests
import pytest
from unittest.mock import Mock
from datetime import date

import sys
sys.path.insert(0, '../collection')
import symbol_change_query

#class TestSymbolChangeQueryMethods(unittest.TestCase):
def test_make_queries():
    test_url = 'https://www.test.com/api?key={API_KEY}'
    test_key = 'key'
    expected_query = 'https://www.test.com/api?key=key'
    response_data = [True]
    
    class MockResponse:
        def json(self):
            return response_data
    requests.get = Mock(return_value=MockResponse())
    
    output = symbol_change_query.make_queries(test_url, test_key)
    requests.get.assert_called_with(expected_query)
    assert response_data == output

def test_trim_query_output():
    today = date.today().strftime('%Y-%m-%d')
    test_item = {'date': today, 'oldSymbol': '', 'newSymbol': ''}
    test_input = [test_item, {'date': '1969-01-30', 'oldSymbol': '', 'newSymbol': ''}]
    
    output = symbol_change_query.trim_query_output(test_input)
    assert 1 == len(output)
    assert test_item == output[0]

def test_get_old_name():
    test_symbol = 'AAPL'
    test_name = 'Apple Inc.'
    test_config = [{'stocks': [{'name': test_name, 'symbol': test_symbol}]}]
    
    success_output = symbol_change_query.get_old_name(test_config, test_symbol)
    fail_output = symbol_change_query.get_old_name(test_config, 'APPL')
    assert test_name == success_output
    assert "" == fail_output

def test_modify_output_list():
    date = '3034-01-31'
    new_name = 'AppleSoft Corporation'
    old_name = 'Apple Inc.'
    new_symbol = 'APFT'
    old_symbol = 'AAPL'
    test_list = [{'date': date, 'name': new_name, 'oldSymbol': old_symbol, 'newSymbol': new_symbol}]
    test_config = [{'stocks': [{'name': old_name, 'symbol': old_symbol}]}]
    expected_output = [{"_change_date": date, "_change_newName": new_name, "_change_oldName": old_name, "_change_newSymbol": new_symbol, "_change_oldSymbol": old_symbol}]
    
    output = symbol_change_query.modify_output_list(test_list, test_config)
    assert expected_output == output

def test_modify_system_config():
    test_name = 'AppleSoft Corporation'
    new_symbol = 'APFT'
    old_symbol = 'AAPL'
    test_config = [{'stocks': [{'name': test_name, 'symbol': old_symbol}]}]
    test_changelog = {old_symbol: new_symbol}
    expected_output = [{'stocks': [{'name': test_name, 'symbol': new_symbol}]}]
    print(test_config, test_changelog)
    output = symbol_change_query.modify_system_config(test_config, test_changelog)
    assert expected_output == output

