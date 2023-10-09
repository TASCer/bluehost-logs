import datetime as dt
# import ipwhois
import logging
from src import my_secrets

from datetime import datetime
# from ipwhois.utils import get_countries
# from ipwhois import IPWhois
from logging import Logger
from sqlalchemy.engine import Engine, CursorResult
from sqlalchemy import exc, create_engine, text
from typing import Optional, Any

now: datetime = dt.datetime.now()
todays_date: str = now.strftime('%D').replace('/', '-')

# COUNTRIES = get_countries()


def update(ips: list) -> object:
    """Takes in list of unique source ip addresses and ipdates lookup table to have country name added later"""
    logger: Logger = logging.getLogger(__name__)
    try:
        engine: Engine = create_engine(f"mysql+pymysql://{my_secrets.dbuser}:{my_secrets.dbpass}@{my_secrets.dbhost}/{my_secrets.dbname}")

    except exc.SQLAlchemyError as e:
        logger.critical(str(e))
        engine = None
        exit()
    # ISSUE CHECK IF ALREADY FOUND COUNTRY NAME
    with engine.connect() as conn, conn.begin():
        for ip in ips:
            ins_sql = conn.execute(text(f'''INSERT IGNORE into `bluehost-logs`.lookup values('{ip}', 'tbd');'''))
