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
		filename = path+month+'-'+str(now.year)
		print(filename)

		# if not platform.system() == 'Windows':
		# 	try:
		# 		os.system(f'scp {path} {my_secrets.local_dir}')
		# 		logger.info(f"{path} {my_secrets.local_dir} retrieved from bh server")
		# 	except (BaseException, FileNotFoundError) as e:
		# 		logger.critical(f"{path} LOG NOT RETRIEVED. Investigate")
		# else:
		# 	try:
		# 		os.system(f'pscp {my_secrets.user}@{my_secrets.bh_ip}:{filename}.gz ../input/zipped/')
		# 		logger.info(f"{path} {my_secrets.local_dir} retrieved from bh server")
		# 	except (BaseException, FileNotFoundError) as e:
		# 		logger.critical(f"{path} LOG NOT RETRIEVED. Investigate")

		with gzip.open('../input/zipped/roadspies.cag.bis.mybluehost.me-ssl_log-Jan-2024.gz') as zipped_file:
			with open(f"../input/roadspies", 'wb') as unzipped_file:
				unzipped_file.write(zipped_file.read())

		# else:
		# 	try:
		# 		shutil.copy(path, my_secrets.local_dir)
		#
		# 	except (IOError, FileNotFoundError) as e:
		# 		logger.error(e)

