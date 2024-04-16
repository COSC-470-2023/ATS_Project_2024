from unittest.mock import MagicMock, patch

from ats.database import bonds_insert


def test_check_keys():
    entry = {
        '_bond_date': 'test value',
        '_test': 'test value'
    }
    row = bonds_insert.check_keys(entry)
    assert len(row) == 13
    assert '_bond_date' in row
    assert row['_bond_date'] == 'test value'
    assert '_test' not in row


@patch('ats.database.bonds_insert.sqlalchemy')
def test_execute_insert(mock_sqlalchemy):
    entry = {
        '_bond_date': None
    }
    modified_entry = entry | {'bond_id': 42}
    mock_check_keys = MagicMock()
    mock_check_keys.return_value = entry
    bonds_insert.check_keys = mock_check_keys
    mock_sqlalchemy.text.return_value = 'test query'
    mock_response = MagicMock()
    mock_response.scalar.return_value = 1
    mock_connection = MagicMock()
    mock_connection.execute.return_value = mock_response
    bonds_insert.execute_insert(mock_connection, entry, 42)
    mock_check_keys.assert_called_with(entry)
    mock_connection.execute.assert_called_with('test query', modified_entry)
    mock_response.scalar.return_value = 0
    bonds_insert.execute_insert(mock_connection, entry, 42)
    assert mock_sqlalchemy.text.call_count == 3
    assert mock_connection.execute.call_count == 3
    mock_connection.execute.assert_called_with('test query', modified_entry)


@patch('ats.database.bonds_insert.sqlalchemy')
def test_get_bond_id(mock_sqlalchemy):
    entry = {
        '_bond_name': 42
    }
    mock_sqlalchemy.text.return_value = 'test query'
    mock_response = MagicMock()
    mock_response.one_or_none.return_value = ['test id one or none']
    mock_connection = MagicMock()
    mock_connection.execute.return_value = mock_response
    bond_id = bonds_insert.get_bond_id(entry, mock_connection)
    mock_connection.execute.assert_called_with('test query')
    assert bond_id == 'test id one or none'
    mock_response.one_or_none.return_value = None
    mock_response.one.return_value = ['test id one']
    bond_id = bonds_insert.get_bond_id(entry, mock_connection)
    assert mock_sqlalchemy.text.call_count == 4
    assert mock_connection.execute.call_count == 4
    mock_connection.execute.assert_called_with('test query')
    assert bond_id == 'test id one'
