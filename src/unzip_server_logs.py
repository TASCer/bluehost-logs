import datetime as dt
import gzip
import logging
import my_secrets
import os
import platform

from datetime import datetime
from logging import Logger

logger: Logger = logging.getLogger(__name__)

now: datetime = dt.datetime.now()


def process(files: list[str], *args) -> set:
	"""
	Takes in a list of paths for location of website log files
	If historical
	param: paths
	param: month
	param: year
	"""

	local_files = set()

	for file in files:
		# Unzip file save to unzipped
		month_num = now.month
		month_name = now.strftime('%b')
		year = str(now.year)

		try:
			local_file = file.split('.')[0]
			with gzip.open(f'{my_secrets.local_zipped_path}{file}', 'rb') as zipped_file:
				with open(f"{my_secrets.local_unzipped_path}{local_file}_{month_name}-{year}", 'wb') as unzipped_file:
					unzipped_file.write(zipped_file.read())
		except (BaseException, FileNotFoundError) as e:
			logger.critical(f"{e}")

		local_files.add(local_file)

	return local_files