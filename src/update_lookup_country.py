import datetime as dt
import ipwhois
import logging
from src import my_secrets

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
LOOKUP = 'lookup'

COUNTRIES = get_countries()


def get(unique_ips: list):
    """Updates lookup table SOURCE entries with full country name and ASN Description"""
    logger: Logger = logging.getLogger(__name__)
    country_found: list = []
    country_not_found: list = []

    try:
        engine: Engine = create_engine(f"mysql+pymysql://{my_secrets.dbuser}:{my_secrets.dbpass}@{my_secrets.dbhost}/{my_secrets.dbname}")

    except exc.SQLAlchemyError as e:
        logger.critical(str(e))
        engine = None
        exit()

    with engine.connect() as conn, conn.begin():
            logger.info("Updating lookup table with source country name and description via IPWhois")

            try:
                sql_no_country: CursorResult = conn.execute(text(f'''SELECT * from {LOOKUP} WHERE COUNTRY = '' or COUNTRY is null;'''))
                no_country: list = [i for i in sql_no_country]
            except exc.SQLAlchemyError as e:
                logger.warning(str(e))

            for ip, country, code, desc in no_country:
                try:
                    obj: IPWhois = ipwhois.IPWhois(ip, timeout=10)
                    result: dict = obj.lookup_rdap()

                except (UnboundLocalError, ValueError, AttributeError, ipwhois.BaseIpwhoisException, ipwhois.ASNLookupError,
                        ipwhois.ASNParseError, ipwhois.ASNOriginLookupError, ipwhois.ASNRegistryError,
                        ipwhois.HostLookupError, ipwhois.HTTPLookupError) as e:
                    logger.error(f'{e}')
                    continue

                asn_description: str = result['asn_description']

                if asn_description == "NA" or asn_description is None:
                    asn_description = "NA"
                else:
                    asn_description = asn_description.rsplit(',')[0]

                if result['asn_country_code'] is None:
                    logger.warning(f"{ip} had no alpha2 code, setting country name to 'unknown'")
                    asn_alpha2: str = '00'
                    conn.execute(text(f'''update lookup SET country = '{asn_alpha2}' WHERE SOURCE = '{ip}';'''))
                    continue

                elif result['asn_country_code'].islower():
                    asn_alpha2: str = asn_alpha2.upper()
                    logger.warning(f'RDAP responded with lowercase country for {ip}, should be upper')

                else:
                    asn_alpha2 = result['asn_country_code']
                    country_name: Optional[str] = COUNTRIES.get(asn_alpha2)

                try:
                    conn.execute(text(f'''UPDATE `{my_secrets.dbname}`.`{LOOKUP}`
                            SET
                                `COUNTRY` = '{country_name}',
                                `ALPHA2` = '{asn_alpha2}',
                                `DESCRIPTION` = '{asn_description}'
                            WHERE `SOURCE` = '{ip}';'''
                                  ))
                except exc.ProgrammingError as e:
                    logger.error(e)

    logger.info(f"Lookup table updated {len(no_country)} with country names and ASN description")
