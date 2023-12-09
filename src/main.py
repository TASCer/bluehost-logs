# TODO THINGS SEEM TO WORK, DO MORE TESTING and fully populate lookup country, create db backups. Start fresh in 2024
import datetime as dt
import db_checks
import logging
import my_secrets
import parse_logs
import re
import inserts_activity_table
import update_lookup_country
import inserts_lookup_table

# from collections import namedtuple
from logging import Logger, Formatter

now: dt = dt.date.today()
todays_date: str = now.strftime('%D').replace('/', '-')

root_logger: Logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

fh = logging.FileHandler(f'../log_{todays_date}.log')
fh.setLevel(logging.DEBUG)

formatter: Formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)

root_logger.addHandler(fh)

logger: Logger = logging.getLogger(__name__)


if __name__ == '__main__':
	logger.info("Checking RDBMS Availability")
	have_database: bool = db_checks.schema()
	have_tables: bool = db_checks.tables()
	if have_database and have_tables:
		logger.info("RDBMS is available and ready")
	else:
		logger.error(f"RDBMS IS NOT OPERATIONAL: RDBMS: {have_database} / TABLES: {have_tables}")
	ips, processed_logs = parse_logs.process()
	unique_sources: set = set(ips)
	logger.info(f"HITS: {len(processed_logs)} Unique HITS: {len(unique_sources)}")
	inserts_lookup_table.update(unique_sources)
	update_lookup_country.get(unique_sources)
	inserts_activity_table.update(processed_logs)
