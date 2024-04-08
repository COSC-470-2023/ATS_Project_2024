import datetime
import sqlalchemy
from sqlalchemy import create_engine, text
import os

from ats.globals import DIR_DATABASE, DIR_DATA_COLLECTION, LOG_FILE
from ats.util import connect
from ats import loguru_init

# loguru initialization
logger = loguru_init.initialize()

# sql query
insert_query = text(
    "INSERT INTO `system_logs` (`date`, `timezone`, `level`, `message`) VALUES (:date, :timezone, :level, :message)"
)

# db params
db_params = {
    "user": os.getenv("ATS_DBMS_USER"),
    "host": os.getenv("ATS_LOGS_HOST"),
    "pass": os.getenv("ATS_LOGS_PASS"),
    "database": os.getenv("ATS_LOGS_DATABASE"),
}


def parse_log(line):
    """
    :param line: The particular line of the log file currently being parsed
    :return: Dictionary of key:value pairs for each part of the log
    """
    # Specify format by splitting line into parts
    parts = line.split("|")
    if len(parts) < 3:
        return None

    date, timezone = parts[0].strip().rsplit(" ", 1)
    level = parts[1].strip()
    message = parts[2].strip()
    # print(f'date: {date} timezone: {timezone} level: {level} message: {message}')
    return {
        "date": date,
        "timezone": timezone,
        "level": level,
        "message": message[:400],
    }


def main():
    # Setup database connection using sqlalchemy
    sql_port = 3306
    uri = f"mysql+pymysql://{db_params['user']}:{db_params['pass']}@{db_params['host']}:{sql_port}/{db_params['database']}"
    engine = sqlalchemy.create_engine(uri)

    # Log paths from both collection and database directories
    log_files = [
        os.path.join(DIR_DATABASE, LOG_FILE),
        os.path.join(DIR_DATA_COLLECTION, LOG_FILE),
    ]

    # connect, no need to close manually
    connection = engine.connect()

    try:
        with connection as conn:
            with connection.begin():
                for path in log_files:
                    if os.path.exists(path):
                        # Load log file from LOG_FILE
                        with open(path, "r") as file:
                            for line in file:
                                log_entry = parse_log(line)
                                if log_entry:
                                    conn.execute(
                                        insert_query, log_entry
                                    )  # parameters=log_entry[line]
    except Exception as e:
        logger.critical(f"Error when connecting to remote database: {e}")


if __name__ == "__main__":
    main()
