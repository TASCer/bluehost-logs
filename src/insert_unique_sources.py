import datetime as dt
import logging
import my_secrets

from datetime import datetime
from logging import Logger
from sqlalchemy.engine import Engine
from sqlalchemy import exc, create_engine, text

now: datetime = dt.datetime.now()
todays_date: str = now.strftime("%D").replace("/", "-")

# SQL TABLE constants
SOURCES = "sources"


def update(unique_ips: set) -> None:
    """
    Updates lookup table with unique sources
    :param: set
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
        for ip in unique_ips:
            conn.execute(text(f"""INSERT IGNORE into {SOURCES} values('{ip}', '', '', '');"""))
