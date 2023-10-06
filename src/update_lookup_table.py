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
from typing import Optional, Any

now: datetime = dt.datetime.now()
todays_date: str = now.strftime('%D').replace('/', '-')

COUNTRIES = get_countries()


def update(ips: list) -> object:
    """Updates lookup table with unique ips from ALPHA-2 to full country name"""
    logger: Logger = logging.getLogger(__name__)
    try:
        engine: Engine = create_engine(f"mysql+pymysql://{my_secrets.fwlogs_dbuser}:{my_secrets.fwlogs_dbpass}@{my_secrets.fwlogs_dbhost}/{my_secrets.fwlogs_dbname}")

    except exc.SQLAlchemyError as e:
        logger.critical(str(e))
        engine = None
        exit()

    with engine.connect() as conn, conn.begin():
        country_found = []
        country_not_found = []
        for ip in ips:
            # get country name from fwlogs.lookup to populate bluehost_logs.lookup
            try:
                sel_sql: str = f'''SELECT country from lookup WHERE source = '{ip}' ;'''
                lookups: CursorResult = conn.execute(text(sel_sql))
                res = [i[0] for i in lookups]
            except exc.SQLAlchemyError as e:
                logger.warning(str(e))
                lookups = None
                exit()
            if res:
                # insert ip, country into bluehost_lookup table
                country_name = res[0]
                logger.info(f"**{country_name} @ {ip} was found in SOHO firewall logs**")
                country_found.append((ip, country_name))

            # else:
            #     # print("COUNTRY NOT FOUND")
            #     country_name = 'NF'
            #     country_not_found.append((ip, country_name))

    print(len(country_found), country_found)
    print(len(country_not_found), country_not_found)

    try:
        engine: Engine = create_engine(f"mysql+pymysql://{my_secrets.dbuser}:{my_secrets.dbpass}@{my_secrets.dbhost}/{my_secrets.dbname}")

    except exc.SQLAlchemyError as e:
        logger.critical(str(e))
        engine = None
        exit()

    with engine.connect() as conn, conn.begin():

        for ip, country in country_not_found:
            print(ip, country)
            try:
                obj: IPWhois = ipwhois.IPWhois(ip, timeout=10)
                result: dict = obj.lookup_rdap()
                asn_alpha2: str = result['asn_country_code']

                if asn_alpha2 is None or asn_alpha2 == '':
                    logger.warning(f"{ip} had no alpha2 code, setting country name to 'unknown'")
                    asn_alpha2: str = 'unknown'
                    conn.execute(f'''update lookup SET country = '{asn_alpha2}' WHERE SOURCE = '{ip}';''')
                    continue

                elif asn_alpha2.islower():
                    asn_alpha2: str = asn_alpha2.upper()
                    logger.warning(f'RDAP responded with lowercase country for {ip}, should be upper')

                else:
                    country_name: Optional[Any] = COUNTRIES.get(asn_alpha2)

            except (UnboundLocalError, ValueError, AttributeError, ipwhois.BaseIpwhoisException, ipwhois.ASNLookupError,
                    ipwhois.ASNParseError, ipwhois.ASNOriginLookupError, ipwhois.ASNRegistryError,
                    ipwhois.HostLookupError, ipwhois.HTTPLookupError) as e:

                result = None
                error: str = str(e).split('http:')[0]
                logger.error(f"{error} {ip}")

            conn.execute(text(f'''INSERT INTO `bluehost-logs`.`lookup` VALUES('{ip}', '{country}');'''))

        #         conn.execute(f'''update lookup SET country = '{error}' WHERE SOURCE = '{ip}';''')
        #         continue
        #

        #

        #
        #     if not country_name:
        #         logger.warning("Country Name not found in COUNTRIES, setting it to alpha-2")
        #         conn.execute(f'''update lookup SET country = '{asn_alpha2}' WHERE SOURCE = '{ip}';''')
        #         continue
        #
        #     elif "'" in country_name:
        #         country_name = country_name.replace("'", "''")
        #         logger.warning(f"Apostrophe found in {country_name}")
        #         conn.execute(f'''update lookup SET country = '{country_name}' WHERE SOURCE = '{ip}';''')
        #
        #     else:
        #         conn.execute(f'''update lookup SET country = '{country_name}' WHERE SOURCE = '{ip}';''')
