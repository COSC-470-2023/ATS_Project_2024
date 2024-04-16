from typing import Callable, TypeAlias

from ats.logger import Logger

logger = Logger.instance()

# Constants
ENTRY = 'entry'
KEY_NOT_FOUND = 'key not found'

Entry: TypeAlias = dict
Kwargs: TypeAlias = dict[str, Entry]
MappingCallback: TypeAlias = Callable[[Entry], ...]


class Mapping:
    """
    A class to manage field mappings, allowing transformation of raw data.
    """
    def __init__(self):
        self.mapping = {}

    def add(self, field: str, callback: MappingCallback):
        """
        Adds a mapping from a data field to a callback function that processes data for that field.
        :param field: The field name for the mapping to apply.
        :param callback: callback function that will process data.
        """
        self.mapping[field] = callback

    def lookup(self, field: str, *args):
        """
        Executes the callback tied to the given field.
        :param field: The given field name.
        :return: result of the callback function.
        """
        cb = self.mapping[field]
        return cb(*args)


def mapping_callback(cb: Callable[[Kwargs], ...]) -> MappingCallback:
    """
    Decorator to transform a simple function into a MappingCallback.
    :param cb: The callback function that processes the data.
    :return: A wrapper function.
    """
    def wrapper(entry: Entry = None):
        kwargs = {
            ENTRY: entry,
        }
        return cb(kwargs)
    return wrapper


def process_raw_data(raw_data: list[dict],
                     api_fields: dict[str, str],
                     non_api_fields: list[str] = None,
                     mapping: Mapping = None,
                     entry_key: str = None) -> list[dict]:
    """
    Processes a list of raw data entries according to specified field and non-api-field mappings.
    :param raw_data: A JSON representing raw data entries.
    :param api_fields: A dictionary mapping raw data fields to processed data fields.
    :param non_api_fields: A list of fields not provided by the API.
    :param mapping: A Mapping object for non-API fields.
    :param entry_key: Optional key to handle nested data structures.
    :return: A list of processed dictionaries.
    """
    data = []

    def helper(raw_entry_sub: dict = None):
        entry = process_entry(raw_entry,
                              api_fields,
                              non_api_fields,
                              mapping,
                              raw_entry_sub)
        data.append(entry)

    for raw_entry in raw_data:
        if entry_key:
            for res in raw_entry[entry_key]:
                helper(res)
        else:
            helper()

    return data


def process_entry(raw_entry: dict,
                  api_fields: dict[str, str],
                  non_api_fields: list[str] = None,
                  mapping: Mapping = None,
                  raw_entry_sub: dict = None):
    """
    Processes an individual entry from raw data.

    :param raw_entry: The dictionary containing raw data.
    :param api_fields: A dictionary mapping raw data fields to their new keys.
    :param non_api_fields: A list of fields not provided by the API, that must be Mapped.
    :param mapping: A Mapping object for non-api-fields.
    :param raw_entry_sub: Optional dictionary for nested data.
    :return: A dictionary of the processed entry.
    """
    processed_entry = {}

    for field_name in api_fields:
        new_field = api_fields[field_name]
        if field_name in raw_entry:
            processed_entry[new_field] = raw_entry[field_name]
        elif raw_entry_sub and field_name in raw_entry_sub:
            processed_entry[new_field] = raw_entry_sub[field_name]
        else:
            logger.warning("Key(s) missing in entry, skipping")
            continue

    if non_api_fields and mapping:
        for field_name in non_api_fields:
            value = mapping.lookup(field_name, raw_entry)
            if value != KEY_NOT_FOUND:
                processed_entry[field_name] = value
            else:
                logger.warning("Key(s) missing in entry, skipping")
                continue

    return processed_entry
