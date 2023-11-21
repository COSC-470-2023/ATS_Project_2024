"""
connection function, creates engine and returns connection object
decorator allows use of the context manager to close the connection automatically
could also be a class, but we'll leave it as a function unless there needs to be enough data attached to it to justify it
"""

from contextlib import contextmanager
from database.processing import credentials as cred

from sqlalchemy import column
from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy import table
from sqlalchemy import text


@contextmanager
def connect():
    try:
        sql_port = 3306
        # database uri - connector://user:pass@hostname:sql_port(3306 by default)/database
        uri = f"mysql+pymysql://{cred.db['user']}:{cred.db['pass']}@{cred.db['host']}:{sql_port}/{cred.db['database']}"
        # create engine
        # echo=True for sql feedback on every op
        engine = create_engine(uri)
        # connect, no need to close manually
        connection = engine.connect()
        # generator - like a return with iteration, allows function to continue from a previous state after a return
        yield connection
    except Exception as error:
        print(error)

    finally:
        # block executed when closed by context manager, as the with statement is really just a try/finally block
        connection.close()
