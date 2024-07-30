import re

from parse_logs import LogEntry


with open(r"../assets/sample_unzipped_logfile") as logs:
    for log in logs:
        basic: str = log.split('" "')[0]
        ip: str = basic.split("- - ")[0]
        SOURCE: str = ip.rstrip()
        basic_info: str = basic.split("- - ")[1]
        server_timestamp: str = basic_info.split("]")[0][1:]

        action1: str = basic_info.split('"')[1]

        try:
            ACTION, FILE, TYPE = action1.split(" ")

        except (ValueError, IndexError) as e:
            continue

        if "'" in FILE:
            FILE = FILE.replace("'", "")

        if len(FILE) >= 120:
            try:
                action_list: str = FILE.split("?")
                action_file1: str = action_list[0]
                action_file2: str = action_list[1][:80]

            except IndexError:
                try:
                    action_list: str = FILE.split("+")
                    action_file1: str = action_list[0]
                    action_file2 = ""

                except IndexError as e:
                    print(f"{e}")

            FILE = action_file1 + action_file2 + " *TRUNCATED*"

        try:
            action2 = basic_info.split('"')[2].strip()
            RES_CODE, SIZE = action2.split(" ")

        except ValueError as e:
            continue

        agent_info = log.split('" "')[1]
        agent_list = agent_info.split(" ")
        AGENT = agent_list[0].replace('"', "")

        if AGENT.startswith("-"):
            AGENT: str = "NA"

        elif AGENT.startswith("'"):
            AGENT = AGENT.replace("'", "")

        REF_IP: str = agent_list[-1].strip()
        REF_URL: str = agent_list[-2]

        # finds all between (    )
        client: list = re.findall(r"\((.*?)\)", log)

        if not client:
            CLIENT, client_format = 2 * ("NA",)

        elif len(client) == 1:
            client_os = client[0]
            CLIENT = client_os.replace(";", "")

        else:
            client_os = client[0]
            CLIENT = client_os.replace(";", "")

        if "'" in CLIENT:
            CLIENT = CLIENT.replace("'", "")

        entry = LogEntry(
            server_timestamp=server_timestamp,
            SOURCE=SOURCE,
            ACTION=ACTION,
            FILE=FILE,
            TYPE=TYPE,
            REF_URL=REF_URL,
            REF_IP=REF_IP,
            RES_CODE=RES_CODE,
            SIZE=SIZE,
            AGENT=AGENT,
            CLIENT=CLIENT,
        )
        print(entry.SOURCE)
