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

new_line = '\n'


def process_logs():
	log_entries: list = []
	sources: list = []
	with open('tests/test_hoa_sslOct-2023') as logs:
		for log in logs:
			basic = log.split('" "')[0]
			ip = basic.split("- - ")[0]
			ip = ip.rstrip()

			# skip parsing system cron jobs on server
			if ip == f'{my_secrets.bh_home_ip}':
				continue

			basic_info = basic.split("- - ")[1]
			server_timestamp: str = basic_info.split(']')[0][1:]

			action1 = basic_info.split('"')[1]
			action, action_file, action_http_ver = action1.split(' ')

			if len(action_file) >= 120:
				action_file = action_file.split('?')[0]
				logger.warning(f"{ip} had too long file request")

			action2 = basic_info.split('"')[2].strip()

			action_code, action_size = action2.split(' ')
			agent_info = log.split('" "')[1]
			agent_list = agent_info.split(' ')
			agent_name = agent_list[0]

			if agent_name.startswith('-'):
				agent_name = "NA"

			referer_ip = agent_list[-1].strip()
			referer_url = agent_list[-2]

			# finds everything between all(    )
			client: list = re.findall("\((.*?)\)", log)

			if not client:
				logger.info(f"NO client info for: {ip}")
				client_os, client_format = 2 * ('NA',)

			elif len(client) == 1:
				client_format = 'NA'
				client_os = client[0]
			else:
				client_os = client[0]
				client_format = client[1]

			print(f"ip: {ip}{new_line}client_os: {client_os}{new_line}client_format: {client_format}{new_line}agent_name: {agent_name}{new_line}")
			print("-------------------------------------------------------")
			sources.append(ip)
			log_entries.append((ip, server_timestamp, action, action_file, action_http_ver, referer_url, referer_ip, action_code, action_size))

	return sources, log_entries


if __name__ == '__main__':
	logger: Logger = logging.getLogger(__name__)
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
	update_lookup_country.find(unique_sources)
	update_activity_table.update(processed_logs)
