# TODO THINGS SEEM TO WORK, DO MORE TESTING and fully populate lookup country, create db backups. Start fresh in 2024
import datetime as dt
import db_checks

import logging
import my_secrets
import re
import update_activity_table
import update_lookup_country
import update_lookup_table

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


def process_logs():
	log_entries: list = []
	sources: list = []
	with open('tests/test_tascsMay-2023-ISSUES') as logs:
		for log in logs:
			basic = log.split('" "')[0]
			ip = basic.split("- - ")[0]
			ip = ip.rstrip()

			# skip parsing system cron jobs on server or activity from my home office
			if ip == f'{my_secrets.bh_home_ip}' or ip == f'{my_secrets.home_ip}':
				continue

			basic_info = basic.split("- - ")[1]
			server_timestamp: str = basic_info.split(']')[0][1:]

			try:
				action1 = basic_info.split('"')[1]
				action, action_file, action_http_ver = action1.split(' ')

			except ValueError as e:
				logger.error(f"{ip}--{e}")
				continue

			if len(action_file) >= 120:
				action_list = action_file.split('?')
				action_file1 = action_list[0]
				action_file2 = action_list[1][:80]
				action_file = action_file1+action_file2+' *TRUNCATED*'
				logger.warning(f"{ip} had too long requested file name, truncated")


			try:
				action2 = basic_info.split('"')[2].strip()
				action_code, action_size = action2.split(' ')

			except ValueError as e:
				logger.error(e, "Possible bot, check logs")
				continue


			agent_info = log.split('" "')[1]
			agent_list = agent_info.split(' ')
			agent_name = agent_list[0].replace('"', '')

			if agent_name.startswith('-'):
				agent_name = "NA"

			referer_ip = agent_list[-1].strip()
			referer_url = agent_list[-2]

			# finds everything between all(    )
			client: list = re.findall("\((.*?)\)", log)

			if not client:
				client_os, client_format = 2 * ('NA',)

			elif len(client) == 1:
				client_format = 'NA'
				client_os = client[0]
				client_os = client_os.replace(';', '')

			else:
				client_os = client[0]
				client_os = client_os.replace(';', '')
				client_format = client[1]

			sources.append(ip)
			log_entries.append((ip, server_timestamp, action, action_file, action_http_ver, referer_url, referer_ip, action_code, action_size, agent_name, client_os))

	return sources, log_entries


if __name__ == '__main__':
	logger.info("Checking RDBMS Availability")
	have_database: bool = db_checks.schema()
	have_tables: bool = db_checks.tables()

	if have_database and have_tables:
		logger.info("RDBMS is available and ready")
	else:
		logger.error(f"RDBMS IS NOT OPERATIONAL: RDBMS: {have_database} / TABLES: {have_tables}")

	ips, processed_logs = process_logs()
	unique_sources: set = set(ips)
	logger.info(f"HITS: {len(processed_logs)} Unique HITS: {len(unique_sources)}")
	update_lookup_table.update(unique_sources)
	update_lookup_country.get(unique_sources)
	update_activity_table.update(processed_logs)
