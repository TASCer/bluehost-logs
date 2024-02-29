# TODO create db backups. Start fresh in 2024
import datetime as dt
import db_checks
import get_server_logs
import logging
import mailer
import my_secrets
import parse_logs
import insert_activity
import unzip_server_logs
import update_sources_country
import insert_unique_sources

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

# SERVER log paths less month-year
tascs_logs_path = my_secrets.tascs_logs_zipped
hoa_logs_path = my_secrets.hoa_logs_zipped
roadspies_logs_path = my_secrets.roadspies_logs_zipped
tascs_logs_historical_path = my_secrets.tascs_logs_historical_zipped

remote_log_file_paths = [tascs_logs_path, hoa_logs_path, roadspies_logs_path]
# historical_remote_log_file_paths = [tascs_logs_historical_path}

if __name__ == '__main__':
	logger.info("Checking RDBMS Availability")
	month_num: int = None
	year: str = None
	have_database: bool = db_checks.schema()
	have_tables: bool = db_checks.tables()

	if have_database and have_tables:
		logger.info("RDBMS is available and ready")
	else:
		logger.error(f"RDBMS IS NOT OPERATIONAL: RDBMS: {have_database} / TABLES: {have_tables}")
	logger.info("***** STARTING LOG PROCESSING *****")

	local_zipped_logfiles: list[str] = get_server_logs.secure_copy(remote_log_file_paths, month_num, year)
	local_unzipped_logfiles: list[str] = unzip_server_logs.process(local_zipped_logfiles)

	ips, processed_logs, my_processed_logs = parse_logs.process(local_unzipped_logfiles)
	unique_sources: set = set(ips)
	insert_unique_sources.update(unique_sources)
	update_sources_country.get(unique_sources)
	insert_activity.update(processed_logs, my_processed_logs)
	logger.info("***** COMPLETED WEB LOG PROCESSING *****")
	mailer.send_mail(f"Bluehost log processing complete. Public: {len(processed_logs)} - SOHO: {len(my_processed_logs)}")


