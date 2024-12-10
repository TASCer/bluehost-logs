import logging
import my_secrets

from dateutil.parser import parse
from datetime import datetime

from logging import Logger
from sqlalchemy.engine import Engine
from sqlalchemy import exc, create_engine, text

# SQL TABLE constants
LOGS = "logs"
MY_LOGS = "my_logs"


def parse_timestamp(ts: str) -> datetime:
    """
    Function takes in a str from log file and returns a datetime
    :param ts:
    :return: datetime
    """
    ts = ts.replace(":", " ", 1)
    ts_split = ts.split(" ", 2)
    ts = " ".join(ts_split[0:2])
    ts_parsed = parse(ts)

    return ts_parsed


def update(log_entries: list, my_log_entries: list) -> None:
    """
    Function takes in list of:
    -public log entries
    -SOHO/testing log entries
    Inserts log entries into their respective tables
    """
    logger: Logger = logging.getLogger(__name__)
    try:
        engine: Engine = create_engine(
            f"mysql+pymysql://{my_secrets.dbuser}:{my_secrets.dbpass}@{my_secrets.dbhost}/{my_secrets.dbname}"
        )

    except exc.SQLAlchemyError as e:
        logger.critical(str(e))
        exit()

    with engine.connect() as conn, conn.begin():
        for (
            ts,
            ip,
            client,
            agent_name,
            action,
            file,
            conn_type,
            action_code,
            action_size,
            ref_url,
            ref_ip,
        ) in log_entries:
            ts_parsed = parse_timestamp(ts)

            try:
                conn.execute(
                    text(
                        f"""INSERT IGNORE INTO {LOGS} VALUES('{ts_parsed}', '{ip}', '{client}', '{agent_name}', '{action}', '{file}', '{conn_type}', '{action_code}', '{action_size}', '{ref_url}', '{ref_ip}');"""
                    )
                )
            except (exc.SQLAlchemyError, exc.ProgrammingError, exc.DataError) as e:
                logger.error(e)

    logger.info(f"{len(log_entries)} entries added to {LOGS} table")

    with engine.connect() as conn, conn.begin():
        for (
            ts,
            ip,
            client,
            agent_name,
            action,
            file,
            conn_type,
            action_code,
            action_size,
            ref_url,
            ref_ip,
        ) in my_log_entries:
            ts_parsed = parse_timestamp(ts)

            try:
                conn.execute(
                    text(
                        f"""INSERT IGNORE INTO {MY_LOGS} VALUES('{ts_parsed}', '{ip}', '{client}', '{agent_name}', '{action}', '{file}', '{conn_type}', '{action_code}', '{action_size}', '{ref_url}', '{ref_ip}');"""
                    )
                )
            except (exc.SQLAlchemyError, exc.ProgrammingError, exc.DataError) as e:
                logger.error(e)

    logger.info(f"{len(my_log_entries)} entries added to {MY_LOGS} table")
