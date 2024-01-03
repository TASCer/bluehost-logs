import datetime as dt
import gzip
import logging
import my_secrets
import os
import shutil
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
		local_unzipped_filename = remote_zipped_filename.split()
		local_filename = path+month+'-'+str(now.year)
		local_filename = local_filename.split("/")[1]
		print(remote_zipped_filename, local_filename)

		if not platform.system() == 'Windows':
			try:
				os.system(f'scp {path} {my_secrets.local_dir}')
				logger.info(f"{path} {my_secrets.local_dir} retrieved from bh server")
			except (BaseException, FileNotFoundError) as e:
				logger.critical(f"{path} LOG NOT RETRIEVED. Investigate")
		else:
			try:
				os.system(f'pscp {my_secrets.user}@{my_secrets.bh_ip}:{remote_zipped_filename} {my_secrets.local_zipped_path}')
				logger.info(f"{path} {local_filename} retrieved from bh server")
			except (BaseException, FileNotFoundError) as e:
				logger.critical(f"{e}")

		# with gzip.open(f'{my_secrets.local_zipped_path}{local_filename}.gz') as zipped_file:
		# 	with open(f"{local_unzipped_filename}{local_filename}", 'wb') as unzipped_file:
		# 		unzipped_file.write(zipped_file.read())
