import datetime as dt
import ipwhois
import logging
import time

from dateutil.parser import *
from datetime import datetime
from src import my_secrets
from ipwhois.utils import get_countries
from ipwhois import IPWhois
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
        for ip, ts in log_entries:
            ts = ts.replace(':', ' ', 1)
            date, time, tz = ts.split()
            print("ORIG DATE: ", date)
            print("ORIG TIME: ", time)
            date_obj = parse(date)
            print("PARSED DATE: ", date_obj)
            time_obj = parse(time)#datetime.strptime(time, '%HH::%mm::%S')
            print("PARSED TIME: ", time_obj)
            # date = datetime.strptime(date, "")
            # ts = parse(ts)
            # print(ip, ts, type(ts))
            conn.execute(text(f'''INSERT INTO `bluehost-logs`.`activity` VALUES(id, '{ip}', '{date_obj}', '{time_obj}');'''))

