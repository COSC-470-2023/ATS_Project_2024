import re
from typing import Callable, Protocol

import requests

from ats.logger import Logger

logger = Logger.instance()

# Constants
API_KEY = '{API_KEY}'
TOKEN_REGEX = r'{\w+}'


class QueryManager:
    """
    Manages the construction and storage of query URLs for API calls, replacing placeholders with actual parameters.
    :param endpoint: The base URL of the API endpoint.
    :param api_key: The API key to be used.
    """
    def __init__(self, endpoint: str, api_key: str):
        self.endpoint = endpoint.replace(API_KEY, api_key)
        self.tokens = re.findall(TOKEN_REGEX, self.endpoint)
        self.queries = []

    def add(self, *args: str):
        """
        Replace tokens in the endpoint with actual parameters to form query URLs.
        :param args: Arguments that replace the tokens.
        """
        query = self.endpoint
        for i in range(len(self.tokens)):
            query = query.replace(self.tokens[i], args[i])
        self.queries.append(query)

    def get(self):
        """
        Retrieve list of constructed queries. If no queries were added, returns a list containing the original endpoint.
        :return: A list of complete queries.
        """
        if not self.queries:
            return [self.endpoint]
        return self.queries


class QueryBuilder(Protocol):
    def __call__(self, queries: QueryManager, *args): ...


class Fetcher:
    """
    Responsible for fetching data from an API using constructed query from QueryManager.
    :param endpoint: The base URL of the API endpoint.
    :param api_key: The API key.
    :param build_queries: A callable that takes a QueryManager and optional additional arguments to construct queries.
    """
    def __init__(self,
                 endpoint: str,
                 api_key: str,
                 build_queries: QueryBuilder = None):
        self.endpoint = endpoint
        self.api_key = api_key
        self.build_queries = build_queries

    def fetch(self, *args) -> list[dict]:
        """
        Execute the API queries and return the data as a list of dictionaries (JSON).
        :param args: Arguments to be used for dynamically building the query if necessary.
        :return: A JSON containing the API dataset.
        """
        logger.info('Executing query')
        raw_data = []
        queries = QueryManager(self.endpoint, self.api_key)

        if self.build_queries:
            self.build_queries(queries, *args)
        elif args:
            queries.add(*args)

        try:
            for query in queries.get():
                response = requests.get(query)
                json = response.json()
                if isinstance(json, list):
                    for entry in json:
                        if 'Error Message' in entry:
                            logger.error(f"api_error {json}")
                            raise Exception
                        raw_data.append(entry)
                else:
                    if 'Error Message' in json:
                        logger.error(f"api_error {json}")
                        raise Exception
                    raw_data.append(json)
        except requests.RequestException as e:
            logger.debug(f"api_error {e}")

        logger.success('Query successful')
        return raw_data


def query_builder(cb: Callable[..., None]) -> QueryBuilder:
    """
    Decorator for transforming a simple callable into a QueryBuilder-compliant callable.
    :param cb: The callback function to be transformed.
    :return: A callable that can be used as a QueryBuilder.
    """
    def wrapper(queries: QueryManager, *args):
        cb(queries, *args)
    return wrapper
