import argparse
import datetime as dt
import db_checks
import fetch_server_logs
import insert_activity
import insert_unique_sources
import logging
import mailer
import my_secrets
import parse_logs
import unzip_fetched_server_logs
import update_sources_whois

from logging import Logger, Formatter

now: dt = dt.date.today()
todays_date: str = now.strftime("%D").replace("/", "-")

root_logger: Logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

fh = logging.FileHandler(f"../{todays_date}.log")
fh.setLevel(logging.DEBUG)

formatter: Formatter = logging.Formatter("%(asctime)s - %(name)s -%(lineno)d - %(levelname)s - %(message)s")
fh.setFormatter(formatter)

root_logger.addHandler(fh)

logger: Logger = logging.getLogger(__name__)

# REMOTE BLUEHOST LOG PATHS EXCEPT "month-year"
remote_tascs_logpath = my_secrets.tascs_logs_zipped
remote_hoa_logpath = my_secrets.hoa_logs_zipped
remote_roadspies_logpath = my_secrets.roadspies_logs_zipped
remote_logfile_paths = [remote_tascs_logpath, remote_hoa_logpath, remote_roadspies_logpath]

remote_historical_logpath = my_secrets.tascs_logs_historical_zipped
remote_historical_logpaths = [remote_historical_logpath]


def database_check() -> None:
    """
    Function checks if database schema and tables are available
    :return: None
    """
    logger.info("Checking RDBMS Availability")
    have_database: bool = db_checks.schema()
    have_tables: bool = db_checks.tables()

    if have_database and have_tables:
        logger.info("RDBMS ONLINE")
        return True

    else:
        logger.error(f"**RDBMS OFFLINE: {have_database} / TABLES: {have_tables}**")
        return False


def main(month_num: int | None, year: int | None) -> None:
    logger.info("***** STARTING WEBLOG PROCESSING *****")
    if year and month_num:
        dt_string: str = f"{year}-{month_num}-01"
        dt_obj: dt = dt.datetime.strptime(dt_string, "%Y-%m-%d")
        month_name: str = dt_obj.strftime("%b")
        year: str = str(year)

    else:
        month_name: str = now.strftime("%b")
        year: str = str(now.year)

    local_zipped_logfiles: set[str] = fetch_server_logs.secure_copy(
        remote_logfile_paths, month_name, year
    )
    local_unzipped_logfiles: set[str] = unzip_fetched_server_logs.process(
        local_zipped_logfiles, month_name, year
    )

    ips, processed_logs, my_processed_logs = parse_logs.process(
        local_unzipped_logfiles, month_name, year
    )

    unique_sources: set = set(ips)
    insert_unique_sources.update(unique_sources)
    update_sources_whois.lookup()
    insert_activity.update(processed_logs, my_processed_logs)

    logger.info("***** COMPLETED WEB LOG PROCESSING *****")

    mailer.send_mail(
        "BH WebLog Processing Complete",
        f"Public: {len(processed_logs)} - SOHO: {len(my_processed_logs)}",
    )


if __name__ == "__main__":
    rdbms: bool = database_check()
    if rdbms:
        parser = argparse.ArgumentParser(description="ADHOC month/year log processing")
        parser.add_argument(
            "-m",
            "--month_num",
            type=int,
            choices=[m for m in range(1, 13)],
            help="Enter a Month number: 1-12",
        )
        parser.add_argument(
            "-y",
            "--year",
            type=int,
            choices=[y for y in range(2019, now.year + 1)],
            help="Enter full year i.e: 2022",
        )
        args = parser.parse_args()

        main(**vars(args))
