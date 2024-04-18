from unittest.mock import MagicMock, patch

from ats.database import symbol_change_update


@patch('ats.database.symbol_change_update.sqlalchemy')
def test_update_symbol(mock_sqlalchemy):
    symbol = {
        '_change_newName': 'Banana Inc.',
        '_change_oldSymbol': 'AAPL',
        '_change_newSymbol': 'BBNA'
    }
    mock_sqlalchemy.text.return_value = 'test query'
    mock_connection = MagicMock()
    symbol_change_update.update_symbol(mock_connection, symbol)
    mock_connection.execute.assert_called_with('test query', parameters=symbol)
