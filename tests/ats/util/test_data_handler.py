from unittest.mock import MagicMock

from ats.util import data_handler


def test_mapping():
    mapping = data_handler.Mapping()
    assert mapping.mapping == {}
    mapping_callback = MagicMock()
    mapping.add('foo', mapping_callback)
    assert mapping.mapping == {'foo': mapping_callback}
    mapping_callback.return_value = 'Success'
    lookup = mapping.lookup('foo')
    assert lookup == 'Success'


def test_mapping_callback_decorator():
    mock_cb = MagicMock()
    mock_entry = MagicMock()
    wrapper = data_handler.mapping_callback(mock_cb)
    wrapper(mock_entry)
    mock_cb.assert_called_with({data_handler.ENTRY: mock_entry})


def test_process_raw_data():
    raw_data = [{'old': 'foo'}, {'old': 'bar'}]
    api_fields = {'old': 'new'}
    data = data_handler.process_raw_data(raw_data, api_fields)
    assert data == [{'new': 'foo'}, {'new': 'bar'}]
    non_api_fields = ['baz']
    mock_mapping = MagicMock()
    mock_mapping.lookup.return_value = 'qux'
    data = data_handler.process_raw_data(raw_data,
                                         api_fields,
                                         non_api_fields,
                                         mock_mapping)
    assert data == [{'new': 'foo', 'baz': 'qux'}, {'new': 'bar', 'baz': 'qux'}]

# TODO: process raw data with sub-entries
