# TODO issues with field data -- hoa seems to work, tascssolutions not so much
import datetime as dt
import db_checks

import logging
import my_secrets
import re
import update_activity_table
import update_lookup_country
import update_lookup_table

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
	with open('../tests/test_tascsolutions_sslOct-2023') as logs:
		for log in logs:
			basic = log.split('" "')[0]
			basic_info = basic.split("- - ")[1]
			server_timestamp: str = basic_info.split(']')[0][1:]

			ip = basic.split("- - ")[0]
			ip = ip.rstrip()

			if ip == f'{my_secrets.home_ip}':  # skip cron jobs on my server
				continue
			# find everything between (    )
			client = re.findall("\((.*?)\)", log)

			if not client:
				print("NO '()'! ")
				client_os, client_format = 2 * ('',)

			# if len(client) == 0:
				# print(f"{ip} has issue with client re pattern, alter re to resolve")
			elif len(client) == 1:
				client_format = ''
				client_os = client[0]
			else:
				client_os = client[0]
				client_format = client[1]
			# find all "xxxxx"
			action = re.findall('\"(.*?\")', basic)
			action_info = action[0]
			action_info = action_info.split()
			action_verb = action_info[0]
			action_file = action_info[1].replace('/', '')
			action_http_ver = action_info[2]

			agent_info = log.split('" "')[1]
			agent_list = agent_info.split(' ')
			agent_name = agent_list[0]

			if agent_name.startswith('-'):
				agent_name = "ERROR"

			agent_referer_ip = agent_list[-1].strip()
			agent_referer_url = agent_list[-2]
			# print(f"ip: {ip}{new_line}country: {country}{new_line}date: {date}{new_line}time: {time}{new_line}client_os: {client_os}{new_line}client_format: {client_format}{new_line}"
			# 	  f"action verb: {action_verb}{new_line}action_file: {action_file}{new_line}action_http_ver: {action_http_ver}{new_line}agent_name: {agent_name}"
			# 	  f"{new_line}agent_referer_ip: {agent_referer_ip}{new_line}agent_referer_url: {agent_referer_url}{new_line}")
			# f"action verb: {action_verb}{new_line}action_file: {action_file}{new_line}action_http_ver: {action_http_ver}")
			# print(f"{ip}\t\t {agent_name}")
			# print("-------------------------------------------------------")
			sources.append(ip)
			log_entries.append((ip, server_timestamp))
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
	logger.info(f"HITS: {len(processed_logs)}")
	unique_sources: set = set(ips)
	logger.info(f"HITS: {len(processed_logs)} Unique HITS: {len(unique_sources)}")
	# country_not_found: list = get_country_name.find(unique_sources)
	update_lookup_table.update(unique_sources)
	update_lookup_country.find(unique_sources)


