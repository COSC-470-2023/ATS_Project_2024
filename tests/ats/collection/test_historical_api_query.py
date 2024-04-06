import datetime
from unittest.mock import MagicMock, call

from ats.collection import historical_api_query


def test_build_queries():
    mock_query_manager = MagicMock()
    config_data = [
        {historical_api_query.SYMBOL: 'AAPL'},
        {historical_api_query.SYMBOL: 'MSFT'}
    ]
    days = 100
    start_date = datetime.date(1936, 8, 4)
    end_date = datetime.date(1936, 11, 12)
    historical_api_query.build_queries(mock_query_manager,
                                       config_data,
                                       days,
                                       end_date)
    calls = [
        call.add('AAPL', str(start_date), str(end_date)),
        call.add('MSFT', str(start_date), str(end_date))
    ]
    mock_query_manager.assert_has_calls(calls)


def test_make_mapping():
    name = 'AppleSoft Conglomerate'
    config_data = [
        {historical_api_query.SYMBOL: 'AAFT',
         historical_api_query.NAME: name},
    ]
    mapping = historical_api_query.make_mapping(config_data)
    entry = {historical_api_query.SYMBOL: 'AAFT'}
    assert mapping.lookup(historical_api_query.HISTORICAL_NAME, entry) == name
