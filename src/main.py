import my_secrets
import re

new_line = '\n'


# hoa seems to wotk, tascs not so much
def process_logs():
	# remove = string.punctuation
	log_entries = []
	with open('../test/tascsolutions_sslOct-2023') as logs:
		for log in logs:
			basic = log.split('" "')[0]
			ip = basic.split("- - ")[0]
			ip = ip.rstrip()
			# skip cron jobs on my server
			if ip == f'{my_secrets.home_ip}':
				continue

			client = re.findall("\((.*?)\)", log)

			if len(client) == 0:
				client_os, client_format  = 2*('', )
				print(f"{ip} has issue with client split, alter re to resolve")
			elif len(client) == 1:
				client_format = ''
				client_os = client[0]
			else:
				client_os = client[0]
				client_format = client[1]

			action = re.findall('\"(.*?\")', basic)
			action_info = action[0]
			action_info = action_info.split()
			action_verb = action_info[0]
			action_file = action_info[1].replace('/', '')
			action_http_ver = action_info[2]

			agent_info = log.split('" "')[1]

			# query_ip = IPWhois(ip)
			# res = query_ip.lookup_rdap()

			country = "TEST" # res['asn_country_code']

			basic_info = basic.split("- - ")[1]

			ts = basic_info.split(']')[0][1:]
			date, time = ts.split(':', 1)

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
			print("-------------------------------------------------------")
			log_entries.append(ip)
	# with open engine as conn, conn.begin


	return log_entries


if __name__ == '__main__':
	processed_logs: list = process_logs()
	print(f"HITS: {len(processed_logs)}")
	unique_processed_logs: set = set(processed_logs)
	print(f"Unique HITS: {len(unique_processed_logs)}")
	# update_country_name(entries)
