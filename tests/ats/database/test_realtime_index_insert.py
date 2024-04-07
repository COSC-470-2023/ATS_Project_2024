from unittest.mock import MagicMock, patch

from ats.database import realtime_index_insert


def test_check_keys():
    entry = {
        '_realtime_date': 'test value',
        '_test': 'test value'
    }
    row = realtime_index_insert.check_keys(entry)
    assert len(row) == 14
    assert '_realtime_date' in row
    assert row['_realtime_date'] == 'test value'
    assert '_test' not in row


@patch('ats.database.realtime_index_insert.sqlalchemy')
def test_execute_insert(mock_sqlalchemy):
    entry = {
        '_realtime_date': None
    }
    modified_entry = entry | {'index_id': 42}
    mock_check_keys = MagicMock()
    mock_check_keys.return_value = entry
    realtime_index_insert.check_keys = mock_check_keys
    mock_sqlalchemy.text.return_value = 'test query'
    mock_response = MagicMock()
    mock_response.scalar.return_value = 1
    mock_connection = MagicMock()
    mock_connection.execute.return_value = mock_response
    realtime_index_insert.execute_insert(mock_connection, entry, 42)
    mock_check_keys.assert_called_with(entry)
    mock_connection.execute.assert_called_with('test query', modified_entry)
    mock_response.scalar.return_value = 0
    realtime_index_insert.execute_insert(mock_connection, entry, 42)
    assert mock_sqlalchemy.text.call_count == 3
    assert mock_connection.execute.call_count == 3
    mock_connection.execute.assert_called_with('test query', modified_entry)


@patch('ats.database.realtime_index_insert.sqlalchemy')
def test_get_index_id(mock_sqlalchemy):
    modified_entry = {
        'symbol': 42,
        'name': 65535
    }
    entry = {
        '_realtime_symbol': 42,
        '_realtime_name': 65535,
        '_test': 3
    }
    mock_sqlalchemy.text.return_value = 'test query'
    mock_response = MagicMock()
    mock_response.one_or_none.return_value = ['test id one or none']
    mock_connection = MagicMock()
    mock_connection.execute.return_value = mock_response
    index_id = realtime_index_insert.get_index_id(entry, mock_connection)
    mock_connection.execute.assert_called_with('test query', parameters=modified_entry)
    assert index_id == 'test id one or none'
    mock_response.one_or_none.return_value = None
    mock_response.one.return_value = ['test id one']
    index_id = realtime_index_insert.get_index_id(entry, mock_connection)
    assert mock_sqlalchemy.text.call_count == 3
    assert mock_connection.execute.call_count == 4
    mock_connection.execute.assert_called_with('test query', parameters=modified_entry)
    assert index_id == 'test id one'
