import datetime as dt
# import ipwhois
import logging
# import time

from dateutil.parser import *
from datetime import datetime
from src import my_secrets
from ipwhois.utils import get_countries
# from ipwhois import IPWhois
from logging import Logger
from sqlalchemy.engine import Engine, CursorResult
from sqlalchemy import exc, create_engine, text
from typing import Optional, Any

now: datetime = dt.datetime.now()
todays_date: str = now.strftime('%D').replace('/', '-')

COUNTRIES = get_countries()


def update(log_entries: list) -> object:
    """Updates lookup table with unique ips from ALPHA-2 to full country name"""
    logger: Logger = logging.getLogger(__name__)
    try:
        engine: Engine = create_engine(f"mysql+pymysql://{my_secrets.dbuser}:{my_secrets.dbpass}@{my_secrets.dbhost}/{my_secrets.dbname}")

    except exc.SQLAlchemyError as e:
        logger.critical(str(e))
        engine = None
        exit()

    with engine.connect() as conn, conn.begin():
        for ip, ts, action, file, conn_type, ref_url in log_entries:
            ts_orig = ts.replace(":", " ", 1)
            ts_split = ts_orig.split(" ", 2)
            ts = ' '.join(ts_split[0:2])
            ts_parsed = parse(ts)
            print(ref_url)
            try:
                conn.execute(text(f'''INSERT INTO `bluehost-logs`.`activity` VALUES(id, '{ip}', '{action}', '{file}', '{conn_type}', '{ts_parsed}', '{ref_url}');'''))
            except exc.SQLAlchemyError as e:
                logger.error(str(e))
