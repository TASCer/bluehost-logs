import datetime as dt
import logging
import my_secrets
import sqlalchemy as sa

from logging import Logger
from sqlalchemy import create_engine, exc, types, Column, Table, MetaData, ForeignKey, Index
from sqlalchemy_utils import database_exists, create_database

now = dt.datetime.now()
todays_date = now.strftime('%D').replace('/', '-')

# SQL DB connection constants
DB_HOSTNAME = f'{my_secrets.dbhost}'
DB_NAME = f'{my_secrets.dbname}'
DB_USER = f'{my_secrets.dbuser}'
DB_PW = f'{my_secrets.dbpass}'

# SQL TABLE constants
LOGS = 'logs'
SOURCES = 'sources'
MY_LOGS = 'my_logs'


def schema():
    """Check to see if schema/DB_NAME is present, if not, create"""
    logger: Logger = logging.getLogger(__name__)
    try:
        engine = create_engine(f'mysql+pymysql://{DB_USER}:{DB_PW}@{DB_HOSTNAME}/{DB_NAME}')

        if not database_exists(engine.url):
            create_database(engine.url)

    except (exc.SQLAlchemyError, exc.OperationalError) as e:
        logger.critical(str(e))
        return False

    return True


def tables():
    """
	Check to see if all CONSTANT tables are created
	If not, create them and return True
	Returns False and logs error if issue
    """
    logger: Logger = logging.getLogger(__name__)

    try:
        engine = create_engine(f'mysql+pymysql://{DB_USER}:{DB_PW}@{DB_HOSTNAME}/{DB_NAME}')

    except (exc.SQLAlchemyError, exc.OperationalError) as e:
        logger.critical(str(e))
        return False

    logs_tbl_insp = sa.inspect(engine)
    logs_tbl: bool = logs_tbl_insp.has_table(LOGS, schema=f"{DB_NAME}")
    my_logs_tbl: bool = logs_tbl_insp.has_table(MY_LOGS, schema=f"{DB_NAME}")
    sources_tbl_insp = sa.inspect(engine)
    sources_tbl: bool = sources_tbl_insp.has_table(SOURCES, schema=f"{DB_NAME}")

    meta = MetaData()

    if not logs_tbl:
        try:
            logs = Table(
                LOGS, meta,
                Column('ACCESSED', types.TIMESTAMP(timezone=True), primary_key=True, nullable=False),
                Column('SOURCE', types.VARCHAR(15), ForeignKey("sources.SOURCE"), nullable=False),
                Column('CLIENT', types.VARCHAR(200), primary_key=True, nullable=False),
                Column('AGENT', types.VARCHAR(100), primary_key=True, nullable=False),
                Column('ACTION', types.VARCHAR(12), primary_key=True, nullable=False),
                Column('FILE', types.VARCHAR(120), primary_key=True, nullable=False),
                Column('TYPE', types.VARCHAR(20), primary_key=True, nullable=False),
                Column('CODE', types.VARCHAR(10), primary_key=True, nullable=False),
                Column('SIZE', types.VARCHAR(100), primary_key=True, nullable=False),
                Column('REF_URL', types.VARCHAR(100), primary_key=True, nullable=False),
                Column('REF_IP', types.VARCHAR(100), primary_key=True, nullable=False)
            )
            Index("accessed", logs.c.ACCESSED)

        except (AttributeError, exc.SQLAlchemyError, exc.ProgrammingError, exc.OperationalError) as e:
            logger.error(str(e))
            return False

    if not my_logs_tbl:
        try:
            my_logs = Table(
                MY_LOGS, meta,
                Column('ACCESSED', types.TIMESTAMP(timezone=True), primary_key=True, nullable=False),
                Column('SOURCE', types.VARCHAR(15), ForeignKey("sources.SOURCE"), nullable=False),
                Column('CLIENT', types.VARCHAR(200), primary_key=True, nullable=False),
                Column('AGENT', types.VARCHAR(100), primary_key=True, nullable=False),
                Column('ACTION', types.VARCHAR(12), primary_key=True, nullable=False),
                Column('FILE', types.VARCHAR(120), primary_key=True, nullable=False),
                Column('TYPE', types.VARCHAR(20), primary_key=True, nullable=False),
                Column('CODE', types.VARCHAR(10), primary_key=True, nullable=False),
                Column('SIZE', types.VARCHAR(100), primary_key=True, nullable=False),
                Column('REF_URL', types.VARCHAR(100), primary_key=True, nullable=False),
                Column('REF_IP', types.VARCHAR(100), primary_key=True, nullable=False)
            )
            Index("accessed", my_logs.c.ACCESSED)

        except (AttributeError, exc.SQLAlchemyError, exc.ProgrammingError, exc.OperationalError) as e:
            logger.error(str(e))
            return False

    if not sources_tbl:
        try:

            sources = Table(
                SOURCES, meta,
                Column('SOURCE', types.VARCHAR(15), primary_key=True),
                Column('COUNTRY', types.VARCHAR(100)),
                Column('ALPHA2', types.VARCHAR(2)),
                Column('DESCRIPTION', types.VARCHAR(160))
            )
            Index("country", sources.c.COUNTRY)

        except (AttributeError, exc.SQLAlchemyError, exc.ProgrammingError, exc.OperationalError) as e:
            logger.error(str(e))
            return False

    meta.create_all(engine)

    return True
