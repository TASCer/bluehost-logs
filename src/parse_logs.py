import logging
import my_secrets
import re

from logging import Logger
from typing import NamedTuple

logger: Logger = logging.getLogger(__name__)


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


def process(log_paths: set):
	all_log_entries = []
	all_sources = []
	for p in log_paths:
		logger.info(f"Processing: {p}")
		with open(p) as logs:
			site_log_entries: int = 0
			site_sources: int = 0
			for log in logs:
				basic = log.split('" "')[0]
				ip = basic.split("- - ")[0]
				SOURCE = ip.rstrip()

				# skip parsing system cron jobs on bluehost server or activity from my home office when not testing
				if SOURCE == f'{my_secrets.bh_ip}' or SOURCE == f'{my_secrets.home_ip}':
					continue

				basic_info = basic.split("- - ")[1]
				server_timestamp = basic_info.split(']')[0][1:]

				try:
					action1 = basic_info.split('"')[1]
					ACTION, FILE, TYPE = action1.split(' ')

				except ValueError as e:
					logger.error(f"{ip}--{e}")
					continue

				if len(FILE) >= 120:
					try:
						action_list = FILE.split('?')
						action_file1 = action_list[0]
						action_file2 = action_list[1][:80]
					except IndexError:
						try:
							action_list = FILE.split('+')
							action_file1 = action_list[0]
							action_file2 = ''

						except IndexError as e:
							logger.error(e)

					FILE = action_file1+action_file2+' *TRUNCATED*'
					logger.warning(f"\t\t{SOURCE} had too long requested file name, truncated")

				try:
					action2 = basic_info.split('"')[2].strip()
					RES_CODE, SIZE = action2.split(' ')

				except ValueError as e:
					logger.error("Possible bot, check logs")
					continue

				agent_info = log.split('" "')[1]
				agent_list = agent_info.split(' ')
				AGENT = agent_list[0].replace('"', '')

				if AGENT.startswith('-'):
					AGENT = "NA"

				REF_IP = agent_list[-1].strip()
				REF_URL = agent_list[-2]

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

				site_sources += 1
				all_sources.append(SOURCE)
				entry = LogEntry(SOURCE, server_timestamp, ACTION, FILE, TYPE, REF_URL, REF_IP, RES_CODE, SIZE, AGENT, CLIENT)
				site_log_entries += 1
				all_log_entries.append(entry)
			logger.info(f"\t\t{site_log_entries} logs processed with {site_sources} unique")

	return all_sources, all_log_entries
