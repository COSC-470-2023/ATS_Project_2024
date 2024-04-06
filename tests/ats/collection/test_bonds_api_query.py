import datetime
from unittest.mock import MagicMock, call

from ats.collection import bonds_api_query


def test_build_queries():
    mock_query_manager = MagicMock()
    days = 100
    date = datetime.date(1936, 11, 12)
    bonds_api_query.build_queries(mock_query_manager, days, date)
    calls = [
        call.add(str(datetime.date(1936, 8, 14)),
                 str(datetime.date(1936, 11, 12))),
        call.add(str(datetime.date(1936, 8, 3)),
                 str(datetime.date(1936, 8, 13)))
    ]
    mock_query_manager.assert_has_calls(calls)


def test_make_mapping():
    treasury = 'Pirate Treasury'
    mapping = bonds_api_query.make_mapping(treasury)
    assert mapping.lookup(bonds_api_query.BOND_NAME) == treasury
