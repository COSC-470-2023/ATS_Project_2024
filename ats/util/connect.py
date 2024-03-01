"""
connection function, creates engine and returns connection object
decorator allows use of the context manager to close the connection automatically
could also be a class, but we'll leave it as a function unless there needs to be enough data attached to it to justify it
"""

import os
from contextlib import contextmanager

import sqlalchemy


@contextmanager
def connect():
    username = os.getenv('ATS_DBMS_USER')
    password = os.getenv('ATS_DBMS_PASS')
    hostname = os.getenv('ATS_DBMS_HOST')
    database = os.getenv('ATS_DBMS_DATABASE')
    try:
        sql_port = 3306
        # database uri - connector://user:pass@hostname:sql_port(3306 by default)/database
        uri = f"mysql+pymysql://{username}:{password}@{hostname}:{sql_port}/{database}"
        # create engine
        # echo=True for sql feedback on every op
        engine = sqlalchemy.create_engine(uri)
        # connect, no need to close manually
        connection = engine.connect()
        # generator - like a return with iteration, allows function to continue from a previous state after a return
        yield connection
    except Exception as error:
        print(error)
        raise error  # the blanket exception catching here results in code saying it ran correctly when it didn't without this line
    finally:
        # block executed when closed by context manager, as the with statement is really just a try/finally block
        connection.close()
