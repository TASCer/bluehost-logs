import datetime as dt
import logging
import mailer
import my_secrets
import os
import platform

from logging import Logger

logger: Logger = logging.getLogger(__name__)

now: dt = dt.date.today()
todays_date: str = now.strftime('%D').replace('/', '-')


def secure_copy(paths: list[str], *args: tuple[str, str] | None) -> set:
	"""
	Takes in a list of paths for location of website log files
	If historical
	param: paths
	param: month
	param: year
	"""
	month_num, year = args
	unzipped_paths = set()

	if None not in args:
		month_num, year = args
		dt_string = f"{year}-{month_num}-01"
		dt_obj = dt.datetime.strptime(dt_string, '%Y-%m-%d')
		month_name = dt_obj.strftime('%b')
		year = str(year)

	else:
		month_num = now.month
		month_name = now.strftime('%b')
		year = str(now.year)

	logger.info("STARTED: Copying site log files from remote web server")

	for path in paths:
		remote_zipped_filename = path+month_name+'-'+year+'.gz'

		local_unzipped_filename = remote_zipped_filename.split("/")[1]

		unzipped_paths.add(local_unzipped_filename)

		# COPY FROM REMOTE BLUEHOST SERVER DEPENDING ON PLATFORM
		if not platform.system() == 'Windows':
			try:
				os.system(f'scp {my_secrets.user}@{my_secrets.bh_ip}:{remote_zipped_filename} {my_secrets.local_zipped_path}')
				logger.info(f"{path} {my_secrets.local_zipped_path} retrieved from bluehost server")

			except FileNotFoundError as file_e:
				logger.critical(f"File not found - {file_e}")

			except OSError:
				logger.critical(f"Remote scp issue: {local_unzipped_filename}")
				logger.critical(f"see: scp_errors_{todays_date} for more information")
				mailer.send_mail(f"BH-WEBLOGS ERROR - scp copy. Check log: scp_errors_{todays_date}", f'../log_{todays_date}.log')

				return unzipped_paths

		else:
			try:
				ret_value = os.system(f"pscp -batch {my_secrets.user}@{my_secrets.bh_ip}:{remote_zipped_filename} {my_secrets.local_zipped_path}")
				if ret_value == 1:

					raise os.error

			except os.error:
				try:
					# TRY AGAIN AND CREATE DETAILED LOGFILE
					ret_value = os.system(f"pscp -batch -sshlog pscp_errors_{todays_date} -logappend {my_secrets.user}@{my_secrets.bh_ip}:{remote_zipped_filename} {my_secrets.local_zipped_path}")
					if ret_value == 1:
						raise os.error

				except FileNotFoundError as file_e:
					logger.critical(f"File not found - {file_e}")

				except OSError:
					logger.critical(f"Remote pscp issue: {local_unzipped_filename}")
					logger.critical(f"see: pscp_errors_{todays_date} for more information")
					mailer.send_mail(f"BH-WEBLOGS ERROR - pscp copy. Check log: pscp_errors_{todays_date}", f'../log_{todays_date}.log')

					return unzipped_paths

	logger.info("COMPLETED: Copying site log files from remote web server")

	return unzipped_paths
