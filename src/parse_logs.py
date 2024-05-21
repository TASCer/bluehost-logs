import datetime as dt
import logging
import my_secrets
import re

from logging import Logger
from typing import NamedTuple, Tuple

logger: Logger = logging.getLogger(__name__)

now: dt.datetime = dt.datetime.now()
todays_date: str = now.strftime('%D').replace('/', '-')

month_num: int = now.month
month_name: str = now.strftime('%b')
year: str = str(now.year)


class LogEntry(NamedTuple):
	server_timestamp: str
	SOURCE: str
	CLIENT: str
	AGENT: str
	ACTION: str
	FILE: str
	TYPE: str
	RES_CODE: str
	SIZE: int
	REF_URL: str
	REF_IP: str


def process(log_paths: set) -> Tuple[list[str], list[LogEntry], list[LogEntry]]:
	all_log_entries: list = []
	all_my_log_entries: list = []
	all_sources: list = []
	all_long_files: list = []

	for p in log_paths:
		logger.info(f"Processing: {p}")
		with open(f'{my_secrets.local_unzipped_path}{p}_{month_name}-{year}') as logs:
			site_log_entries: list = []
			site_sources: list = []
			site_long_files: list = []
			site_my_log_entries: list = []

			for log in logs:
				basic: str = log.split('" "')[0]
				ip: str = basic.split("- - ")[0]
				SOURCE: str = ip.rstrip()

				# skip parsing system cron jobs on bluehost server
				if SOURCE == f'{my_secrets.bh_ip}':
					continue

				basic_info: str = basic.split("- - ")[1]
				server_timestamp: str = basic_info.split(']')[0][1:]

				try:
					action1: str = basic_info.split('"')[1]
					ACTION, FILE, TYPE = action1.split(' ')

				except (ValueError, IndexError) as e:
					logger.error(f"\t\tBASIC INFO SPLIT ERROR: {ip}--{e}")
					continue

				if len(FILE) >= 120:
					site_long_files.append(SOURCE)
					all_long_files.append((server_timestamp, SOURCE))

					try:
						action_list: str = FILE.split('?')
						action_file1: str = action_list[0]
						action_file2: str = action_list[1][:80]
					except IndexError:
						try:
							action_list: str = FILE.split('+')
							action_file1: str = action_list[0]
							action_file2 = ''

						except IndexError as e:
							logger.error(e)

					FILE = action_file1+action_file2+' *TRUNCATED*'

				try:
					action2 = basic_info.split('"')[2].strip()
					RES_CODE, SIZE = action2.split(' ')

				except ValueError as e:
					logger.error(f"Possible bot, check logs -> {e}")
					continue

				agent_info = log.split('" "')[1]
				agent_list = agent_info.split(' ')
				AGENT = agent_list[0].replace('"', '')

				if AGENT.startswith('-'):
					AGENT: str = "NA"

				REF_IP: str = agent_list[-1].strip()
				REF_URL: str = agent_list[-2]

				# finds everything between all(    )
				client: list = re.findall("\((.*?)\)", log)

				if not client:
					CLIENT, client_format = 2 * ('NA',)

				elif len(client) == 1:
					client_format = 'NA'
					client_os = client[0]
					CLIENT = client_os.replace(';', '')

				else:
					client_os = client[0]
					CLIENT = client_os.replace(';', '')
					client_format = client[1]

				site_sources.append(SOURCE)
				all_sources.append(SOURCE)
				entry = LogEntry(SOURCE, server_timestamp, ACTION, FILE, TYPE, REF_URL, REF_IP, RES_CODE, SIZE, AGENT, CLIENT)

				if SOURCE == my_secrets.home_ip:
					all_my_log_entries.append(entry)
					site_my_log_entries.append(entry)

				elif SOURCE != my_secrets.home_ip:
					site_log_entries.append(entry)
					all_log_entries.append(entry)

			logger.info(f"\t\t{len(site_log_entries)} NON SOHO logs with {len(set(site_sources))} unique source ip")
			logger.info(f"\t\t{len(site_my_log_entries)} SOHO logs")
			logger.info(f"\t\t{len(site_log_entries) + len(site_my_log_entries)} SITE LOG ENTRIES")

			if len(site_long_files) >= 1:
				logger.warning(f"\t\t{len(site_long_files)} long file names encountered.")

	logger.warning(f"\t\t{len(all_long_files)} LOG ENTRIES HAD FILE NAME OVER 120 chars.")

	return all_sources, all_log_entries, all_my_log_entries
