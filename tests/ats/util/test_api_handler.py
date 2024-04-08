from unittest.mock import MagicMock, patch

from ats.util import api_handler

endpoint = 'https://ats.com/{A}?key={API_KEY}&arg={C}'
api_key = 'bar'


def test_query_manager():
    query_manager = api_handler.QueryManager(endpoint, api_key)
    assert query_manager.endpoint == 'https://ats.com/{A}?key=bar&arg={C}'
    assert query_manager.tokens == ['{A}', '{C}']
    assert not query_manager.queries
    queries = query_manager.get()
    assert len(queries) == 1
    assert queries[0] == 'https://ats.com/{A}?key=bar&arg={C}'
    query_manager.add('foo', 'baz')
    assert len(query_manager.queries) == 1
    assert query_manager.queries[0] == 'https://ats.com/foo?key=bar&arg=baz'
    queries = query_manager.get()
    assert len(queries) == 1
    assert queries[0] == 'https://ats.com/foo?key=bar&arg=baz'


@patch('ats.util.api_handler.requests')
def test_fetcher(mock_requests):
    mock_response = MagicMock()
    mock_response.json.return_value = ['Success']
    mock_requests.get.return_value = mock_response
    fetcher = api_handler.Fetcher(endpoint, api_key)
    assert fetcher.endpoint == endpoint
    assert fetcher.api_key == api_key
    assert not fetcher.build_queries
    data = fetcher.fetch()
    mock_requests.get.assert_called_with('https://ats.com/{A}?key=bar&arg={C}')
    assert data == ['Success']
    data = fetcher.fetch('foo', 'baz')
    mock_requests.get.assert_called_with('https://ats.com/foo?key=bar&arg=baz')
    assert data == ['Success']


@patch('ats.util.api_handler.QueryManager')
def test_fetcher_with_query_builder(mock_query_manager):
    mock_queries = MagicMock()
    mock_query_manager.return_value = mock_queries
    mock_query_builder = MagicMock()
    fetcher = api_handler.Fetcher(endpoint, api_key, mock_query_builder)
    assert fetcher.build_queries == mock_query_builder
    fetcher.fetch('foo', 'baz')
    mock_query_builder.assert_called_with(mock_queries, 'foo', 'baz')


def test_query_builder_decorator():
    mock_cb = MagicMock()
    mock_query_manager = MagicMock()
    wrapper = api_handler.query_builder(mock_cb)
    wrapper(mock_query_manager, 'foo', 'baz')
    mock_cb.assert_called_with(mock_query_manager, 'foo', 'baz')
