import unittest

from sqlalchemy import column, create_engine
from sqlalchemy import select
from sqlalchemy import table
from sqlalchemy import text

from data_collection.collection import historical_api_query


class ConfigLoadTestCase(unittest.TestCase):
    json_config = historical_api_query.load_config()

    def test_url(self):
        expected_url = "https://financialmodelingprep.com/api/v3/historical-price-full/{QUERY_PARAMS}?from={START_DATE}&to={END_DATE}&apikey={API_KEY}"
        retrieved_url = self.json_config[0]['api']  # Get the API field from the loaded JSON
        self.assertEqual(expected_url, retrieved_url, "Retrieved API URL does not match what was expected.")

    def test_api_key(self):
        expected_key = "PASTE KEY HERE"
        retrieved_key = self.json_config[0]['api_key']  # Get the API field from the loaded JSON
        self.assertEqual(expected_key, retrieved_key, "Retrieved API key does not match what was expected.")


if __name__ == '__main__':
    unittest.main()
