import re
from typing import Callable, Protocol

import requests

from ats.logger import Logger

logger = Logger.instance()

# Constants
API_KEY = '{API_KEY}'
TOKEN_REGEX = r'{\w+}'


class QueryManager:
    def __init__(self, endpoint: str, api_key: str):
        self.endpoint = endpoint.replace(API_KEY, api_key)
        self.tokens = re.findall(TOKEN_REGEX, self.endpoint)
        self.queries = []

    def add(self, *args: str):
        query = self.endpoint
        for i in range(len(self.tokens)):
            query = query.replace(self.tokens[i], args[i])
        self.queries.append(query)

    def get(self):
        if not self.queries:
            return [self.endpoint]
        return self.queries


class QueryBuilder(Protocol):
    def __call__(self, queries: QueryManager, *args): ...


class Fetcher:
    def __init__(self,
                 endpoint: str,
                 api_key: str,
                 build_queries: QueryBuilder = None):
        self.endpoint = endpoint
        self.api_key = api_key
        self.build_queries = build_queries

    def fetch(self, *args) -> list[dict]:
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

        logger.info('Query successful')
        return raw_data


def query_builder(cb: Callable[..., None]) -> QueryBuilder:
    def wrapper(queries: QueryManager, *args):
        cb(queries, *args)
    return wrapper
