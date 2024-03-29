import datetime
from unittest.mock import MagicMock, call

from ats.collection import company_info_api_query


def test_build_queries():
    mock_query_manager = MagicMock()
    config_data = [
        {company_info_api_query.SYMBOL: 'AAPL'},
        {company_info_api_query.SYMBOL: 'MSFT'}
    ]
    company_info_api_query.build_queries(mock_query_manager, config_data)
    calls = [call.add('AAPL'), call.add('MSFT')]
    mock_query_manager.assert_has_calls(calls)


def test_make_mapping():
    dt = datetime.datetime.now()
    mapping = company_info_api_query.make_mapping(dt)
    assert mapping.lookup(company_info_api_query.COMPANY_DATE) == str(dt)
