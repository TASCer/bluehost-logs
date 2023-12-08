import logging
import my_secrets
import re

from logging import Logger


logger: Logger = logging.getLogger(__name__)


def process():
	log_entries: list = []
	sources: list = []
	with open('../input/hoa.tascs.net-ssl_log-Dec-2023') as logs:
		for log in logs:
			basic = log.split('" "')[0]
			ip = basic.split("- - ")[0]
			ip = ip.rstrip()

			# skip parsing system cron jobs on bluehost server or activity from my home office when not testing
			# if ip == f'{my_secrets.bh_ip}' or ip == f'{my_secrets.home_ip}':
			# 		continue

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
