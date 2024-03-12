import datetime
import requests
from unittest.mock import MagicMock

from ats.collection import companies_api_query


def test_fetch_company_data():
    api_url = 'https://test.com/api?key={API_KEY}&symbol={STOCK_SYMBOL}'
    api_key = 'key'
    query_items = [{'name': 'DomPre Orichalcum Mining', 'symbol': 'DOM'}]
    expected_query = 'https://test.com/api?key=key&symbol=DOM'

    class MockApiResponse:
        def __init__(self, response):
            self.response = response

        def json(self):
            return self.response
    mock_api_response = MockApiResponse({"success": True})
    requests.get = MagicMock(return_value=mock_api_response)

    output = companies_api_query.fetch_companies_data(api_url, api_key,
                                                      query_items)

    requests.get.assert_called_with(expected_query)
    assert len(output) == 1
    assert len(output[0]) == 1
    assert output[0]['success']


def test_process_companies_data():
    raw_companies_data = [{'field': 1, 'ff': False, 'tf': True},
                          {'field': 2, 'ff': False, 'tf': True}]
    api_fields = {'field': '_test_field', 'ff': None}
    non_api_fields = {
        'mapping': '_company_date',
        'input_type': None,
        'output_type': '_date_time'
    }
    date_time = datetime.datetime.now()

    output = companies_api_query.process_companies_data(raw_companies_data,
                                                        api_fields,
                                                        non_api_fields,
                                                        date_time)

    assert len(output) == 2
    assert len(output[0]) == 3
    assert output[0]['_test_field'] == 1
    assert output[1]['_test_field'] == 2
    assert output[0]['_company_date'] == str(date_time)
    assert output[0]['tf']
