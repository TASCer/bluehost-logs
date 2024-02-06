import datetime as dt
import logging
import mailer
import my_secrets
import os
import platform

from datetime import datetime
from logging import Logger

logger: Logger = logging.getLogger(__name__)

now: datetime = dt.datetime.now()


def secure_copy(paths: list[str], *args) -> set:
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

	logger.info("Copying site log files from remote web server")

	copy_response = 0

	for path in paths:
		remote_zipped_filename = path+month_name+'-'+year+'.gz'

		local_zipped_filename = path + month_name + '-' + year
		local_zipped_filename = local_zipped_filename.split(".")[0].split('/')[1]
		local_unzipped_filename = remote_zipped_filename.split("/")[1]

		unzipped_paths.add(local_unzipped_filename)
		# COPY FROM SERVER
		if not platform.system() == 'Windows':
			try:
				os.system(f'scp {path} {my_secrets.local_zipped_path}')
				# site = my_secrets.
				logger.info(f"{path} {my_secrets.local_zipped_path} retrieved from bh server")
			except (BaseException, FileNotFoundError) as e:
				logger.critical(f"{path} LOG NOT RETRIEVED. Investigate")

		else:
			try:
				ret_value = os.system(f'pscp -batch {my_secrets.user}@{my_secrets.bh_ip}:{remote_zipped_filename} {my_secrets.local_zipped_path}')
				if ret_value == 1:
					copy_response += 1
					raise os.error
					# print(ret_value, type(ret_value))

			except FileNotFoundError as file_e:
				logger.critical(f"File not found - {file_e}")
			except os.error as os_e:
				logger.critical(f"Issue copying remote file for: {local_unzipped_filename}")

	if copy_response == 0:
		return unzipped_paths

	else:
		mailer.send_mail("Error running pscp to Bluehost to get logs. Check log")
		exit()