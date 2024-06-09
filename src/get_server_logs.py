import datetime as dt
import logging
import mailer
import my_secrets
import os
import platform
import subprocess
import time


from logging import Logger

logger: Logger = logging.getLogger(__name__)

now: dt = dt.date.today()
todays_date: str = now.strftime('%D').replace('/', '-')


def secure_copy(paths: list[str], month_name: str | None, year: int | None) -> set:
	"""
	Takes in a list of paths for location of website log files
	If historical
	param: paths
	param: month
	param: year
	"""

	unzipped_paths = set()

	if year and month_name:
		month_name = month_name
		year = year

	else:
		month_name = now.strftime('%b')
		year = str(now.year)

	logger.info("STARTED: Copying site log files from remote web server")

	for path in paths:
		remote_zipped_filename = path+month_name+'-'+year+'.gz'

		local_unzipped_filename = remote_zipped_filename.split("/")[1]

		# COPY FROM REMOTE BLUEHOST SERVER DEPENDING ON PLATFORM
		if not platform.system() == 'Windows':
			try:
				os.system(f'scp {my_secrets.user}@{my_secrets.bh_ip}:{remote_zipped_filename} {my_secrets.local_zipped_path}')
				logger.info(f"{path} {my_secrets.local_zipped_path} retrieved from bluehost server")
				unzipped_paths.add(local_unzipped_filename)

			except FileNotFoundError as file_e:
				logger.critical(f"File not found - {file_e}")

			except OSError:
				logger.critical(f"Remote scp issue: {local_unzipped_filename}")
				logger.critical(f"see: scp_errors_{todays_date} for more information")
				mailer.send_mail(f"BH-WEBLOGS ERROR - scp copy. Check log: scp_errors_{todays_date}", f'../log_{todays_date}.log')

				return unzipped_paths

		else:
			try:
				copy_command = f"pscp -batch {my_secrets.user}@{my_secrets.bh_ip}:{remote_zipped_filename} {my_secrets.local_zipped_path}"
				result = subprocess.check_output(copy_command)
				# time.sleep(3)
				str_result = result.decode(encoding="utf-8")
				logger.info(str_result.strip())
				unzipped_paths.add(local_unzipped_filename)

			except subprocess.CalledProcessError as other_err:
				logger.error(other_err)
				# continue

			except FileNotFoundError as file_e:
				logger.critical(f"File not found - {file_e}")
				continue

	logger.info("COMPLETED: Copying site log files from remote web server")

	return unzipped_paths
