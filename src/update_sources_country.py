import datetime as dt
import ipwhois
import logging
import my_secrets

from datetime import datetime
from ipwhois.utils import get_countries
from ipwhois import IPWhois
from logging import Logger
from sqlalchemy.engine import Engine, CursorResult
from sqlalchemy import exc, create_engine, text
from typing import Optional

now: datetime = dt.datetime.now()
todays_date: str = now.strftime('%D').replace('/', '-')

# SQL TABLE constants
LOGS = 'logs'
SOURCES = 'sources'

COUNTRIES = get_countries()


def get():
    """Updates lookup table SOURCE entries with full country name and ASN Description"""
    logger: Logger = logging.getLogger(__name__)

    http_errors = 0

    try:
        engine: Engine = create_engine(
            f"mysql+pymysql://{my_secrets.dbuser}:{my_secrets.dbpass}@{my_secrets.dbhost}/{my_secrets.dbname}")

    except exc.SQLAlchemyError as e:
        logger.critical(str(e))
        exit()

    with engine.connect() as conn, conn.begin():
        logger.info("Updating lookup table with source country name and description via IPWhois")

        errors = 0

        try:
            sql_no_country: CursorResult = conn.execute(
                text(f'''SELECT * from {SOURCES} WHERE COUNTRY = '' or COUNTRY is null;'''))
            no_country: list = [i for i in sql_no_country]
        except exc.SQLAlchemyError as e:
            logger.warning(str(e))

        for ip, country, code, desc in no_country:
            if ":" in ip:
                logger.warning(f"IPv6 source encountered {ip}")
                continue

            try:
                obj: IPWhois = ipwhois.IPWhois(ip, timeout=10)
                result: dict = obj.lookup_rdap()

            except ipwhois.HTTPLookupError as http:
                http_errors += 1
                http = str(http).split('&')[0]
                conn.execute(text(f'''update {SOURCES} SET country = '{str(http)}' WHERE SOURCE = '{ip}';'''))
                continue

            except (UnboundLocalError, ValueError, AttributeError, ipwhois.BaseIpwhoisException, ipwhois.ASNLookupError,
                    ipwhois.ASNParseError, ipwhois.ASNOriginLookupError, ipwhois.ASNRegistryError,
                    ipwhois.HostLookupError, ipwhois.HTTPLookupError) as e:

                error: str = str(e).split('http:')[0]
                print(f"Non httplookup error: {error} {ip}")
                logger.warning(f"Non httplookup error: {error} {ip}")

                conn.execute(text(f'''update {SOURCES} SET country = '{error}' WHERE SOURCE = '{ip}';'''))
                continue

            asn_description: str = result['asn_description']

            if asn_description == "NA" or asn_description is None:
                asn_description = "NA"
            else:
                asn_description = asn_description.rsplit(',')[0]

            if result['asn_country_code'] is None:
                logger.warning(f"{ip} had no alpha2 code, setting country name to '00'")
                asn_alpha2: str = '00'
                conn.execute(text(f'''update {SOURCES} SET country = '{asn_alpha2}' WHERE SOURCE = '{ip}';'''))
                continue

            elif result['asn_country_code'].islower():
                asn_alpha2: str = asn_alpha2.upper()
                logger.warning(f'RDAP responded with lowercase country for {ip}, should be upper')

            else:
                asn_alpha2 = result['asn_country_code']
                country_name: Optional[str] = COUNTRIES.get(asn_alpha2)

            try:
                conn.execute(text(f'''UPDATE `{my_secrets.dbname}`.`{SOURCES}`
                        SET
                            `COUNTRY` = '{country_name}',
                            `ALPHA2` = '{asn_alpha2}',
                            `DESCRIPTION` = '{asn_description}'
                        WHERE `SOURCE` = '{ip}';'''
                                  ))
            except exc.ProgrammingError as e:
                logger.error(e)

    logger.info(
        f"SOURCES table: {len(no_country) - errors} updated with country names and ASN description. {errors} errors encountered")
