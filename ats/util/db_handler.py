import os
import contextlib

import sqlalchemy

from ats.logger import Logger

logger = Logger.instance()

# Constants
URI_DD = 'mysql+pymysql://'
DBMS_USER = 'ATS_DBMS_USER'
DBMS_PASS = 'ATS_DBMS_PASS'
DBMS_HOST = 'ATS_DBMS_HOST'
DBMS_PORT = 'ATS_DBMS_PORT'
DBMS_DB = 'ATS_DBMS_DATABASE'


class ConnectionManager:
    _instance = None
    uri = None

    def __init__(self):
        raise RuntimeError

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        username = os.getenv(DBMS_USER)
        password = os.getenv(DBMS_PASS)
        hostname = os.getenv(DBMS_HOST)
        port = os.getenv(DBMS_PORT)
        database = os.getenv(DBMS_DB)
        self.uri = (URI_DD
                    + f"{username}:{password}@{hostname}:{port}/{database}")

    @contextlib.contextmanager
    def connect(self):
        connection = None
        try:
            # echo=True for sql feedback on every op
            engine = sqlalchemy.create_engine(self.uri)
            connection = engine.connect()
            yield connection
        except Exception:
            # TODO: log exception
            raise
        finally:
            if connection:
                connection.close()
