import datetime as dt
import logging
import my_secrets
import sqlalchemy as sa

from logging import Logger
from sqlalchemy import create_engine, exc, types, text, Column, Table, MetaData, ForeignKey
from sqlalchemy_utils import database_exists, create_database

now = dt.datetime.now()
todays_date = now.strftime('%D').replace('/', '-')

# SQL DB connection constants
DB_HOSTNAME = f'{my_secrets.dbhost}'
DB_NAME = f'{my_secrets.dbname}'
DB_USER = f'{my_secrets.dbuser}'
DB_PW = f'{my_secrets.dbpass}'
# SQL TABLE constants
ACTIVITY = 'activity'
LOOKUP = 'lookup'


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
	"""Check to see if all CONSTANT tables are created
		If not, create them and return True
		Returns False if error in creating
    """
	logger: Logger = logging.getLogger(__name__)

	try:
		engine = create_engine(f'mysql+pymysql://{DB_USER}:{DB_PW}@{DB_HOSTNAME}/{DB_NAME}')

	except (exc.SQLAlchemyError, exc.OperationalError) as e:
		logger.critical(str(e))
		return False

	activity_tbl_insp = sa.inspect(engine)
	activity_tbl: bool = activity_tbl_insp.has_table(ACTIVITY, schema=f"{DB_NAME}")
	lookup_tbl_insp = sa.inspect(engine)
	lookup_tbl: bool = lookup_tbl_insp.has_table(LOOKUP, schema=f"{DB_NAME}")

	meta = MetaData()

	if not activity_tbl:
		try:
			activity = Table(
				ACTIVITY, meta,
				Column('id', types.INT, autoincrement=True, primary_key=True),
				Column('SOURCE', types.VARCHAR(15)),
				Column('ACTION', types.VARCHAR(12)),
				Column('FILE', types.VARCHAR(120)),
				Column('TYPE', types.VARCHAR(20)),
				Column('ACCESSED', types.TIMESTAMP(timezone=True)),
				Column('REF_URL', types.VARCHAR(100))
			)
		except (exc.SQLAlchemyError, exc.ProgrammingError, exc.OperationalError) as e:
			logger.error(str(e))
			return False

	if not lookup_tbl:

		lookup = Table(
			LOOKUP, meta,
			Column('SOURCE', types.VARCHAR(15), primary_key=True),
			Column('COUNTRY', types.VARCHAR(120)),
			Column('DESCRIPTION', types.VARCHAR(120))
		)
	meta.create_all(engine)

	return True