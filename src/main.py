import argparse
import datetime as dt
import db_checks
import get_server_logs
import insert_activity
import insert_unique_sources
import logging
import mailer
import my_secrets
import parse_logs
import unzip_server_logs
import update_sources_country

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

# REMOTE BLUEHOST LOG PATHS EXCEPT month-year
tascs_logs_path = my_secrets.tascs_logs_zipped
hoa_logs_path = my_secrets.hoa_logs_zipped
roadspies_logs_path = my_secrets.roadspies_logs_zipped
tascs_logs_historical_path = my_secrets.tascs_logs_historical_zipped

remote_log_file_paths = [tascs_logs_path, hoa_logs_path, roadspies_logs_path]
historical_remote_log_file_paths = [tascs_logs_historical_path]


def main(month_num: int | None, year: int | None) -> None:
    if year and month_num:
        dt_string: str = f"{year}-{month_num}-01"
        dt_obj: dt = dt.datetime.strptime(dt_string, "%Y-%m-%d")
        month_name: str = dt_obj.strftime("%b")
        year: str = str(year)

    else:
        month_name: str = now.strftime("%b")
        year: str = str(now.year)

    local_zipped_logfiles: set[str] = get_server_logs.secure_copy(
        remote_log_file_paths, month_name, year
    )
    local_unzipped_logfiles: set[str] = unzip_server_logs.process(
        local_zipped_logfiles, month_name, year
    )

    ips, processed_logs, my_processed_logs = parse_logs.process(
        local_unzipped_logfiles, month_name, year
    )

    unique_sources: set = set(ips)
    insert_unique_sources.update(unique_sources)
    update_sources_country.get()
    insert_activity.update(processed_logs, my_processed_logs)

    logger.info("***** COMPLETED WEB LOG PROCESSING *****")

    mailer.send_mail(
        "BH WebLog Processing Complete",
        f"Public: {len(processed_logs)} - SOHO: {len(my_processed_logs)}",
    )


if __name__ == "__main__":
    logger.info("Checking RDBMS Availability")
    have_database: bool = db_checks.schema()
    have_tables: bool = db_checks.tables()

    if have_database and have_tables:
        logger.info("RDBMS is available and ready")
    else:
        logger.error(f"RDBMS IS NOT OPERATIONAL: RDBMS: {have_database} / TABLES: {have_tables}")

    logger.info("***** STARTING WEBLOG PROCESSING *****")

    parser = argparse.ArgumentParser(description="One-Off month/year orocessing")
    parser.add_argument(
        "-m",
        "--month_num",
        type=int,
        choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        help="Enter a Month number: 1-12",
    )
    parser.add_argument(
        "-y",
        "--year",
        type=int,
        choices=[2019, 2020, 2021, 2022, 2023, 2024],
        help="Enter full year i.e: 2022",
    )

    args = parser.parse_args()

    main(**vars(args))
