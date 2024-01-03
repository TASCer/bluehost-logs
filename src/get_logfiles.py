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
todays_date: str = now.strftime('%D').replace('/', '-')
month_num = now.month
month = now.strftime('%b')


def secure_copy(paths: list[str]) -> None:
	"""
	Takes in a list of string paths
	"""
	for path in paths:
		remote_zipped_filename = path+month+'-'+str(now.year)+'.gz'

		local_zipped_filename = path + month + '-' + str(now.year)
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
				logger.info(f"{path} {remote_zipped_filename} retrieved from bh server")
			except (BaseException, FileNotFoundError) as e:
				logger.critical(f"{e}")

		print(f'{my_secrets.local_zipped_path}{local_zipped_filename}')

		with gzip.open(f'{my_secrets.local_zipped_path}{local_zipped_filename}.gz') as zipped_file:
			with open(f"{my_secrets.local_unzipped_path}{local_unzipped_filename}", 'wb') as unzipped_file:
				unzipped_file.write(zipped_file.read())
