import datetime

import sqlalchemy
from sqlalchemy import create_engine, text

import os

from ats.globals import DIR_OUT, FN_OUT_LOG_FILE
from ats.util import db_handler
from ats.logger import Logger

# loguru initialization
logger = Logger.instance()
# db connection initialization
connection_manager = db_handler.ConnectionManager.instance()

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
    return {
        "date": date,
        "timezone": timezone,
        "level": level,
        "message": message[:400],
    }


def main():
    # Log paths from both collection and database directories
    log_files = [
        os.path.join(DIR_OUT, FN_OUT_LOG_FILE),
    ]
    logger.info(f"Inserting logs from {log_files} ")

    try:
        with connection_manager.connect() as conn:
            # Begin transaction with context manager, implicit commit on exit or rollback on exception
            with conn.begin():
                for path in log_files:
                    if os.path.exists(path):
                        # Load log file from LOG_FILE
                        with open(path, "r") as file:
                            for line in file:
                                log_entry = parse_log(line)
                                if log_entry:
                                    conn.execute(
                                        insert_query, log_entry
                                    )
        logger.success("Logs Insertion completed successfully")
    except Exception as e:
        logger.critical(f"Error when updating remote database. Exception: {e}")


if __name__ == "__main__":
    main()
