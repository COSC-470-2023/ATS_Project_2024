import json
import unittest

from ats.globals import (DIR_CONFIG, DIR_OUTPUT, CONFIG_REALTIME, OUTPUT_REALTIME_COMMODITIES, OUTPUT_REALTIME_INDEX,
                         OUTPUT_REALTIME_STOCKS)
from ats.util import json_handler


class RealtimeFieldsTest(unittest.TestCase):
    config = json_handler.load_config(DIR_CONFIG + CONFIG_REALTIME)
    # Test designed to work with the first API in the list, update later
    global fields

    # Get the normal API fields
    fields = list(config[0]['api_fields'].values())

    # Get the added fields
    for non_api_field in config[0]['non_api_fields']:
        fields.append(config[0]['non_api_fields'][non_api_field]['mapping'])

    # Remove fields that config set to null/None
    fields = [i for i in fields if i is not None]

    print(f"Testing for fields:\n{json.dumps(fields, indent=2)}")

    def test_stock_fields(self):
        stocks = json_handler.load_config(DIR_OUTPUT + OUTPUT_REALTIME_STOCKS)
        for stock in stocks:
            stock_fields = stock.keys()
            for field in fields:
                self.assertFalse(field not in stock_fields, f"Found missing field {field} in a stock: {stock}")

    def test_commodity_fields(self):
        commodities = json_handler.load_config(DIR_OUTPUT + OUTPUT_REALTIME_COMMODITIES)
        for commodity in commodities:
            commodity_fields = commodity.keys()
            for field in fields:
                if field is not None:
                    self.assertFalse(field not in commodity_fields,
                                     f"Found missing field {field} in a commodity: {commodity}")

    def test_index_fields(self):
        indices = json_handler.load_config(DIR_OUTPUT + OUTPUT_REALTIME_INDEX)
        for index in indices:
            index_fields = index.keys()
            for field in fields:
                if field is not None:
                    self.assertFalse(field not in index_fields, f"Found missing field {field} in a stock: {index}")


if __name__ == '__main__':
    unittest.main()
