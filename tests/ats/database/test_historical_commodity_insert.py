from unittest.mock import MagicMock, patch

from ats.database import historical_commodity_insert


def test_check_keys():
    entry = {
        '_historical_date': 'test value',
        '_test': 'test value'
    }
    row = historical_commodity_insert.check_keys(entry)
    assert len(row) == 12
    assert '_historical_date' in row
    assert row['_historical_date'] == 'test value'
    assert '_test' not in row


@patch('ats.database.historical_commodity_insert.sqlalchemy')
def test_execute_insert(mock_sqlalchemy):
    mock_check_keys = MagicMock()
    mock_check_keys.return_value = {}
    historical_commodity_insert.check_keys = mock_check_keys
    mock_sqlalchemy.text.return_value = 'test query'
    mock_response = MagicMock()
    mock_response.scalar.return_value = 1
    mock_connection = MagicMock()
    mock_connection.execute.return_value = mock_response
    historical_commodity_insert.execute_insert(mock_connection, {}, 42)
    mock_check_keys.assert_called_with({})
    mock_connection.execute.assert_called_with('test query', {'commodity_id': 42})
    mock_response.scalar.return_value = 0
    historical_commodity_insert.execute_insert(mock_connection, {}, 42)
    assert mock_sqlalchemy.text.call_count == 3
    assert mock_connection.execute.call_count == 3
    mock_connection.execute.assert_called_with('test query', {'commodity_id': 42})


@patch('ats.database.historical_commodity_insert.sqlalchemy')
def test_get_commodity_id(mock_sqlalchemy):
    modified_entry = {
        '_historical_symbol': 42,
        '_historical_name': 65535
    }
    entry = modified_entry.copy() | {'_test': 3}
    mock_sqlalchemy.text.return_value = 'test query'
    mock_response = MagicMock()
    mock_response.one_or_none.return_value = ['test id one or none']
    mock_connection = MagicMock()
    mock_connection.execute.return_value = mock_response
    commodity_id = historical_commodity_insert.get_commodity_id(entry, mock_connection)
    mock_connection.execute.assert_called_with('test query', parameters=modified_entry)
    assert commodity_id == 'test id one or none'
    mock_response.one_or_none.return_value = None
    mock_response.one.return_value = ['test id one']
    commodity_id = historical_commodity_insert.get_commodity_id(entry, mock_connection)
    assert mock_sqlalchemy.text.call_count == 3
    assert mock_connection.execute.call_count == 4
    mock_connection.execute.assert_called_with('test query', parameters=modified_entry)
    assert commodity_id == 'test id one'
