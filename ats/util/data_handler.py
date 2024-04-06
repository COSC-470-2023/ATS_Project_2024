from typing import Callable, TypeAlias

from ats.logger import Logger

logger = Logger.instance()

# Constants
ENTRY = 'entry'

Entry: TypeAlias = dict
Kwargs: TypeAlias = dict[str, Entry]
MappingCallback: TypeAlias = Callable[[Entry], ...]


class Mapping:
    def __init__(self):
        self.mapping = {}

    def add(self, field: str, callback: MappingCallback):
        self.mapping[field] = callback

    def lookup(self, field: str, *args):
        cb = self.mapping[field]
        return cb(*args)


def mapping_callback(cb: Callable[[Kwargs], ...]) -> MappingCallback:
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
    # TODO: write docstring
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
    # TODO: write docstring
    processed_entry = {}

    for field_name in api_fields:
        new_field = api_fields[field_name]
        if field_name in raw_entry:
            processed_entry[new_field] = raw_entry[field_name]
        elif raw_entry_sub:
            processed_entry[new_field] = raw_entry_sub[field_name]

    if non_api_fields and mapping:
        for field_name in non_api_fields:
            processed_entry[field_name] = mapping.lookup(field_name, raw_entry)

    return processed_entry
