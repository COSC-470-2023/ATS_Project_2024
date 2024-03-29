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
        return self.mapping[field](*args)


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
                     mapping: Mapping = None) -> list[dict]:
    # TODO: write docstring
    data = []

    for entry in raw_data:
        processed_entry = {}

        for field_name in api_fields:
            new_field = api_fields[field_name]
            processed_entry[new_field] = entry[field_name]

        if non_api_fields and mapping:
            for field_name in non_api_fields:
                processed_entry[field_name] = mapping.lookup(field_name, entry)

        data.append(processed_entry)

    return data
