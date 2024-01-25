import unittest

from sqlalchemy import column, create_engine
from sqlalchemy import select
from sqlalchemy import table
from sqlalchemy import text

from data_collection.collection import realtime_api_query


class ConfigLoadTestCase(unittest.TestCase):
    json_config = realtime_api_query.load_config()

    def test_url(self):
        expected_url = ""
        retrieved_url = self.json_config[0]['api']  # Get the API field from the loaded JSON
        self.assertEqual(expected_url, retrieved_url, "Retrieved API URL does not match what was expected.")

    def test_api_key(self):
        expected_key = "PASTE KEY HERE"
        retrieved_key = self.json_config[0]['api_key']  # Get the API field from the loaded JSON
        self.assertEqual(expected_key, retrieved_key, "Retrieved API key does not match what was expected.")


if __name__ == '__main__':
    unittest.main()
