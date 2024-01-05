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

def secure_copy(paths: list[str], *args) -> None:
	"""
	Takes in a list of paths for location of website log files
	If historical
	param: paths
	param: month
	param: year
	"""
	month_num, year = args

	if not args:
		month_num = now.month
		month_name = now.strftime('%b')
		year = str(now.year)
	else:
		month_num, year = args
		dt_string = f"{year}-{month_num}-01"
		# print(dt_string)
		dt_obj = dt.datetime.strptime(dt_string, '%Y-%m-%d')
		print(dt_obj)
		month_name = dt_obj.strftime('%b')
		year = str(year)

	for path in paths:
		print(month_name, year)
		remote_zipped_filename = path+month_name+'-'+year+'.gz'

		local_zipped_filename = path + month_name + '-' + year
		local_zipped_filename = local_zipped_filename.split("/")[1]
		local_unzipped_filename = remote_zipped_filename.split("/")[1]

		if not platform.system() == 'Windows':
			try:
				os.system(f'scp {path} {my_secrets.local_zipped_path}')
				logger.info(f"{path} {my_secrets.local_zipped_path} retrieved from bh server")
			except (BaseException, FileNotFoundError) as e:
				logger.critical(f"{path} LOG NOT RETRIEVED. Investigate")
		else:
			try:
				os.system(f'pscp {my_secrets.user}@{my_secrets.bh_ip}:{remote_zipped_filename} {my_secrets.local_zipped_path}')

			except (BaseException, FileNotFoundError) as e:
				logger.critical(f"{e}")

		try:
			with gzip.open(f'{my_secrets.local_zipped_path}{local_zipped_filename}.gz') as zipped_file:
				with open(f"{my_secrets.local_unzipped_path}{local_unzipped_filename}", 'wb') as unzipped_file:
					unzipped_file.write(zipped_file.read())
		except (BaseException, FileNotFoundError) as e:
			logger.critical(f"{e}")
