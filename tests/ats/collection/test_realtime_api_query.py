import datetime
from unittest.mock import MagicMock, call

from ats.collection import realtime_api_query


def test_build_queries():
    mock_query_manager = MagicMock()
    config_data = [
        {realtime_api_query.SYMBOL: 'AAPL'},
        {realtime_api_query.SYMBOL: 'MSFT'}
    ]
    realtime_api_query.build_queries(mock_query_manager, config_data)
    calls = [call.add('AAPL'), call.add('MSFT')]
    mock_query_manager.assert_has_calls(calls)


def test_make_mapping():
    dt = datetime.datetime.now()
    mapping = realtime_api_query.make_mapping()
    entry = {realtime_api_query.TIMESTAMP: dt.timestamp()}
    assert mapping.lookup(realtime_api_query.REALTIME_DATE, entry) == str(dt)
