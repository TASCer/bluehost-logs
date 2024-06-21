import datetime as dt
import logging
import my_secrets

from dateutil.parser import *
from datetime import datetime
from ipwhois.utils import get_countries
from logging import Logger
from sqlalchemy.engine import Engine
from sqlalchemy import exc, create_engine, text

now: datetime = dt.datetime.now()
todays_date: str = now.strftime('%D').replace('/', '-')

# SQL TABLE constants
LOGS = 'logs'
MY_LOGS = 'my_logs'
COUNTRIES = get_countries()


def parse_timestamp(ts: str) -> datetime:
    ts = ts.replace(":", " ", 1)
    ts_split = ts.split(" ", 2)
    ts = ' '.join(ts_split[0:2])
    ts_parsed = parse(ts)

    return ts_parsed


def update(log_entries: list, my_log_entries: list) -> None:
    """Updates lookup table with unique ips from ALPHA-2 to full country name"""
    logger: Logger = logging.getLogger(__name__)
    try:
        engine: Engine = create_engine(f"mysql+pymysql://{my_secrets.dbuser}:{my_secrets.dbpass}@{my_secrets.dbhost}/{my_secrets.dbname}")

    except exc.SQLAlchemyError as e:
        logger.critical(str(e))
        # engine = None
        exit()

    with engine.connect() as conn, conn.begin():
        for ts, ip, client, agent_name, action, file, conn_type, action_code, action_size, ref_url, ref_ip in log_entries:
            ts_parsed = parse_timestamp(ts)

            try:
                conn.execute(text(f'''INSERT IGNORE INTO {LOGS} VALUES('{ts_parsed}', '{ip}', '{client}', '{agent_name}', '{action}', '{file}', '{conn_type}', '{action_code}', '{action_size}', '{ref_url}', '{ref_ip}');'''))
            except (exc.SQLAlchemyError, exc.ProgrammingError, exc.DataError) as e:
                logger.error(e)

    logger.info(f"{len(log_entries)} entries added to {LOGS} table")

    with engine.connect() as conn, conn.begin():
        for ts, ip, client, agent_name, action, file, conn_type, action_code, action_size, ref_url, ref_ip in my_log_entries:
            ts_parsed = parse_timestamp(ts)

            try:
                conn.execute(text(f'''INSERT IGNORE INTO {MY_LOGS} VALUES('{ts_parsed}', '{ip}', '{client}', '{agent_name}', '{action}', '{file}', '{conn_type}', '{action_code}', '{action_size}', '{ref_url}', '{ref_ip}');'''))
            except (exc.SQLAlchemyError, exc.ProgrammingError, exc.DataError) as e:
                logger.error(e)

    logger.info(f"{len(my_log_entries)} entries added to {MY_LOGS} table")
