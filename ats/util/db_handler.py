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
    """
    Singleton to manage database connections using SQLAlchemy.
    """
    _instance = None
    uri = None

    def __init__(self):
        """
        WARNING: Do not instantiate this class directly. Use the `instance()` method instead.
        """
        raise RuntimeError

    @classmethod
    def instance(cls):
        """
        Provides a singleton instance of the connection manager.
        :return: instance.
        """
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        """
        Initializes the connection URI from environment variables, forms a db connection string using credentials.
        """
        username = os.getenv(DBMS_USER)
        password = os.getenv(DBMS_PASS)
        hostname = os.getenv(DBMS_HOST)
        port = os.getenv(DBMS_PORT)
        database = os.getenv(DBMS_DB)
        self.uri = (URI_DD
                    + f"{username}:{password}@{hostname}:{port}/{database}")

    @contextlib.contextmanager
    def connect(self):
        """
        Context manager. Establishes a db connection, and closes it when done.
        :yield: A SQLAlchemy connection object that can be used to execute database operations.
        """
        connection = None
        try:
            # # echo=True could be set here if SQL logging is required
            engine = sqlalchemy.create_engine(self.uri)
            connection = engine.connect()
            yield connection
        except Exception as e:
            logger.error(f"Failed to connect to the database: {e}")
            raise
        finally:
            if connection:
                connection.close()
