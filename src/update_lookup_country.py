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


def find():
    """Updates lookup table with unique ips from ALPHA-2 to full country name"""
    logger: Logger = logging.getLogger(__name__)
    country_found = []
    country_not_found = []

    try:
        engine: Engine = create_engine(f"mysql+pymysql://{my_secrets.dbuser}:{my_secrets.dbpass}@{my_secrets.dbhost}/{my_secrets.dbname}")

    except exc.SQLAlchemyError as e:
        logger.critical(str(e))
        engine = None
        exit()

    with engine.connect() as conn, conn.begin():
            try:
                sql_no_country: CursorResult = conn.execute(text('''SELECT * from lookup WHERE COUNTRY = '' ;'''))
                no_country: list = [i for i in sql_no_country]
            except exc.SQLAlchemyError as e:
                logger.warning(str(e))

        # if no_country_name:
            # try:
            #     engine: Engine = create_engine(
            #         f"mysql+pymysql://{my_secrets.dbuser}:{my_secrets.dbpass}@{my_secrets.dbhost}/{my_secrets.dbname}")
            #
            # except exc.SQLAlchemyError as e:
            #     logger.critical(str(e))
            #     engine = None
            #     exit()
            #
            for ip, country in no_country:
                try:
                    obj: IPWhois = ipwhois.IPWhois(ip, timeout=10)
                    result: dict = obj.lookup_rdap()
                    asn_alpha2: str = result['asn_country_code']

                except (UnboundLocalError, ValueError, AttributeError, ipwhois.BaseIpwhoisException, ipwhois.ASNLookupError,
                        ipwhois.ASNParseError, ipwhois.ASNOriginLookupError, ipwhois.ASNRegistryError,
                        ipwhois.HostLookupError, ipwhois.HTTPLookupError) as e:
                    result = None
                    country = asn_alpha2
                    error: str = str(e).split('http:')[0]
                    logger.error(f"{error} {ip}")

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


# else:
    #     country_not_found.append((ip))
    #     logger.info(f"Country Found: {len(country_found)} Not Found: {len(country_not_found)}")

    # NEW ENGINE TO OPS TO ADD TO LOOKUP
    # try:
    #     engine: Engine = create_engine(
    #         f"mysql+pymysql://{my_secrets.dbuser}:{my_secrets.dbpass}@{my_secrets.dbhost}/{my_secrets.dbname}")
    #
    # except exc.SQLAlchemyError as e:
    #     logger.critical(str(e))
    #     engine = None
    #     exit()
    #
    # with engine.connect() as conn, conn.begin():
    #     for s in country_found:
    #         ip = s[0]
    #         country_name = s[1]
    #         conn.execute(text(f'''INSERT IGNORE INTO `bluehost-logs`.`lookup` (`SOURCE`, `COUNTRY`) VALUES ('{ip}', '{country_name}');'''))
    #
    # return country_not_found
        #     use iphois to update lookup with country name
                # try:
                #     obj: IPWhois = ipwhois.IPWhois(ip, timeout=10)
                #     result: dict = obj.lookup_rdap()
                #
                # except (UnboundLocalError, ValueError, AttributeError, ipwhois.BaseIpwhoisException, ipwhois.ASNLookupError,
                #         ipwhois.ASNParseError, ipwhois.ASNOriginLookupError, ipwhois.ASNRegistryError,
                #         ipwhois.HostLookupError, ipwhois.HTTPLookupError) as e:
                #     result = None
                #     error: str = str(e).split('http:')[0]
                #     logger.error(f"{error} {ip}")

            #         conn.execute(f'''update lookup SET country = '{error}' WHERE SOURCE = '{ip}';''')
            #         continue
            #
                # asn_alpha2: str = result['asn_country_code']
            #
                # if asn_alpha2 is None or asn_alpha2 == '':
                #     logger.warning(f"{ip} had no alpha2 code, setting country name to 'unknown'")
                #     asn_alpha2: str = 'unknown'
            #         conn.execute(f'''update lookup SET country = '{asn_alpha2}' WHERE SOURCE = '{ip}';''')
            #         continue
            #
            #     elif asn_alpha2.islower():
            #         asn_alpha2: str = asn_alpha2.upper()
            #         logger.warning(f'RDAP responded with lowercase country for {ip}, should be upper')
            #
            #     else:
            #         country_name: Optional[Any] = COUNTRIES.get(asn_alpha2)
            #
            #     if not country_name:
            #         logger.warning("Country Name not found in COUNTRIES, setting it to alpha-2")
            #         conn.execute(f'''update lookup SET country = '{asn_alpha2}' WHERE SOURCE = '{ip}';''')
            #         continue
            #
            #     elif "'" in country_name:
            #         country_name = country_name.replace("'", "''")
            #         logger.warning(f"Apostrophe found in {country_name}")
            # #         conn.execute(f'''update lookup SET country = '{country_name}' WHERE SOURCE = '{ip}';''')
            #
            #     else:
            #         conn.execute(f'''update lookup SET country = '{country_name}' WHERE SOURCE = '{ip}';''')
