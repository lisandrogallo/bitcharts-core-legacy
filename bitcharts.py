#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Bitcharts - ORM classes and functions
Copyright(c) 2014 - Lisandro Gallo (lisogallo)
liso@riseup.net

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import re
import sys
import smtplib
import requests
import argparse
import simplejson as json
from collections import OrderedDict
from sqlalchemy.engine import Engine
from BeautifulSoup import BeautifulSoup
from ConfigParser import SafeConfigParser
from datetime import date, datetime, timedelta
from sqlalchemy import exc, event, create_engine, ForeignKey, Sequence
from sqlalchemy import Column, Date, Time, Integer, String, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, aliased, sessionmaker


@event.listens_for(Engine, 'connect')
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Decorator to force the support of foreign keys on SQLite.
    :param dbapi_connection: Engine object.
    :param connection_record: Connection string.
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def open_session(engine):
    """
    Open session on current connection and return session object.
    :param engine: Engine object for current connection.
    """
    Session = sessionmaker(bind=engine)
    session = Session()

    return session


def connect_database(database_url):
    """
    Create connection to engine and return engine object.
    :param database_url: Full path URL to SQLite database.
    """
    # Set 'echo' to True to get verbose output.
    engine = create_engine(database_url, echo=False)

    return engine


def create_tables(database_url):
    """
    Create database schema.
    :param database_url: Full path URL to SQLite database.
    """
    engine = connect_database(database_url)
    Base.metadata.create_all(engine)


def config_parser(config_file):
    """
    Parse data from configuration files.
    :param config_file: Configuration file with currencies or exchanges data.
    """
    res = []

    # Parse and read configuration file.
    cparser = SafeConfigParser()
    cparser.read(config_file)

    for section in cparser.sections():
        tup = ()

        for option in cparser.options(section):
            value = cparser.get(section, option)
            # String 'True' or 'False' values to boolean
            if value == 'True':
                value = True
            elif value == 'False':
                value = False
            tup += (value, )
        res.append(tup)

    return res


def send_email(sender, receiver, subject, body):
    """
    Auxiliar function to inform by mail about any unexpected exception.
    :param sender: From mail address.
    :param receiver: Destination mail address.
    :param subject: Subject.
    :param body: Content body.
    """
    try:
        msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s"
            %(sender, receiver, subject, body))
        smtp = smtplib.SMTP('localhost')
        smtp.sendmail(sender, [receiver], msg)
        smtp.quit()

    except Exception as exception:
        print 'Error %s:' % exception.args[0]


def get_json(url):
    """
    Get JSON resource from remote URL.
    :param url: Full URL to JSON resource over HTTP protocol.
    """
    try:
        req = requests.get(url,
                           headers={'Accept': 'application/json'},
                           timeout=5)
        res = req.json()
        return res

    except Exception as exception:
        print 'Error %s:' % exception.args[0]
        send_email(
                    'daemon@bitcharts.org',
                    'staff@bitcharts.org',
                    'ERROR',
                    exception.args[0]
                    )
        res = {}
        return res


def is_dict(something):
    """
    Check if input object is a dictionary or contains a dictionary.
    Return the dictionary found.
    :param something: Input object to check.
    """
    if type(something) is dict:
        for values in something.itervalues():
            if type(values) is dict:
                return is_dict(values)
            return something


def parse_values(dictionary):
    """
    Search for common keys in exchange's APIs which contains currencies values.
    :param dictionary: Dictionary previously obtained from JSON APIs.
    """
    # Check if input is or contains a dictionary and returns it.
    res = is_dict(dictionary)

    # Search for common keys used on APIs and store its values
    if 'last' in res.iterkeys():
        last = float(res.get('last'))
        return last
    elif 'blue' in res.iterkeys():
        blue = float(res.get('blue'))
        return blue


def write_object(database_url, new_object):
    """
    Write new currency, exchange or association object to database through ORM.
    :param database_url: Full path URL to SQLite database.
    :param new_object: Object variable.
    """
    try:
        engine = connect_database(database_url)
        session = open_session(engine)
        session.add(new_object)
        session.commit()

    except exc.SQLAlchemyError, exception:
        if session:
            session.rollback()
        print 'Error %s:' % exception.args[0]
        sys.exit(1)

    finally:
        if session:
            session.close()


def initialize_database(database_url, currencies_file, exchanges_file):
    """
    Initialize Bitcharts database with exchanges and currencies data
    parsed from configuration files.
    :param database_url: Full path URL to SQLite database.
    :param currencies_file: Configuration file with currencies information.
    :param exchanges_file: Configuration file with exchanges information.
    """
    currencies = config_parser(currencies_file)

    # From data in configuration file create each currency ORM object.
    for currency in currencies:
        name, description, cryptocurrency, active = currency
        new_currency = Currency(name,
                                description,
                                cryptocurrency,
                                active)

        write_object(database_url, new_currency)

    try:
        engine = connect_database(database_url)
        session = open_session(engine)

        # From data in configuration file create each currency ORM object.
        exchanges = config_parser(exchanges_file)

        # Open a session and query the associated currency id from the
        # currency name (unique) in the configuration file.
        for exchange in exchanges:
            name, country, url, api, currency_name, active = exchange
            query = session.query(Currency.id).filter(
                Currency.name == currency_name).first()
            currency_id = query[0]
            # From data in configuration file create each currency ORM object.
            new_exchange = Exchange(name,
                                    country,
                                    url,
                                    api,
                                    currency_id,
                                    active)

            write_object(database_url, new_exchange)

    except exc.SQLAlchemyError, exception:
        if session:
            session.rollback()
        print 'Error %s:' % exception.args[0]
        sys.exit(1)

    finally:
        if session:
            session.close()


def clean_database(database_url, days):
    """
    Clean old records from database keeping only the last X days.
    :param database_url: Full path URL to SQLite database.
    :param days: Number of days to keep.
    """
    try:
        engine = connect_database(database_url)
        session = open_session(engine)

        today = date.today()
        last_day = today + timedelta(-int(days))

        query = session.query(Association).filter(
                    Association.date < last_day).all()

        for row in query:
            session.delete(row)

        session.commit()

    except exc.SQLAlchemyError, exception:
        if session:
            session.rollback()
        print 'Error %s:' % exception.args[0]
        sys.exit(1)

    finally:
        if session:
            session.close()


def write_values(database_url):
    """
    Write current currencies values obtained from exchanges as new association
    objects in the ORM.
    :param database_url: Full path URL to SQLite database.
    """
    try:
        engine = connect_database(database_url)
        session = open_session(engine)

        # Store in an intermediate class the current active currencies
        active_currency_ids = aliased(Currency, session.query(Currency)
            .filter(Currency.active == 1).subquery())

        # Store in an intermediate class the current active exchanges
        active_exchange_ids = aliased(Exchange, session.query(Exchange)
            .filter(Exchange.active == 1).subquery())

        # Store in an intermediate class the current active exchanges for
        # current active currencies
        active_currency_exchange_ids = aliased(
        session.query(active_exchange_ids).filter(
        active_exchange_ids.currency_id == active_currency_ids.id)
        .subquery())

        query = session.query(active_currency_exchange_ids).all()

        # Get the active currency values from an active exchange and store
        # data on an association object. Timestamp it is also stored.
        for exchange in query:
            api_url = exchange.url + exchange.api
            from_api = get_json(api_url)
            if from_api:
                last = parse_values(from_api)

                new_assoc = Association(exchange.id,
                                        exchange.currency_id,
                                        last)

                write_object(database_url, new_assoc)

    except exc.SQLAlchemyError, exception:
        print 'Error %s:' % exception.args[0]
        sys.exit(1)

    finally:
        if session:
            session.close()


def write_json_file(ordered_dict, json_path):
    """
    Create database schema.
    :param ordered_dict: Ordered dictionary to be serialized to JSON.
    :param json_path: Fullpath to write serialized JSON in filesystem.
    """
    pretty_json = json.dumps(ordered_dict, sort_keys=False, indent=4 * ' ')

    # Write a pretty formated JSON to a file
    with open(json_path, 'w') as json_file:
        print >> json_file, pretty_json
    json_file.close()


def generate_sources_json(database_url, output_dir):
    """
    Generates a JSON file on filesystem for the Bitcharts' API.
    :param database_url: Full path URL to SQLite database.
    :param output_dir: Output directory to write serialized JSON in filesystem.
    """
    try:
        engine = connect_database(database_url)
        session = open_session(engine)

        # Get current active exchanges
        active_exchange_ids = aliased(Exchange, session.query(Exchange).filter(
            Exchange.active == 1).subquery())

        # query = session.query(Association).all()
        exchanges = session.query(active_exchange_ids).all()

        # Ordered dictionary to be serialized to JSON
        sources_dict = OrderedDict()

        # Show the timestamp on the JSON API
        sources_dict['timestamp'] = datetime.now().strftime(
                                    "%a %b %d %Y, %H:%M:%S")

        # Get a dict for each exchange and append it to the main sources dict
        for exchange in exchanges:
            query = session.query(Association).filter(
        Association.exchange_id == exchange.id).order_by(
        Association.date.desc()).order_by(
        Association.time.desc()).first()
            key_name, row_dict = query.asdict(session)
            sources_dict[key_name] = row_dict

        # Generate JSON file from ordered dictionary
        json_path = output_dir + 'sources.json'
        print 'Generating ' + json_path + ' file...'
        write_json_file(sources_dict, json_path)

    except exc.SQLAlchemyError, exception:
        print 'Error %s:' % exception.args[0]
        sys.exit(1)

    finally:
        if session:
            session.close()


def generate_graphs_json(database_url, output_dir):
    """
    Generates a JSON file on filesystem for the Bitcharts' graphs.
    :param database_url: Full path URL to SQLite database.
    :param output_dir: Output directory to write serialized JSON in filesystem.
    """
    try:
        engine = connect_database(database_url)
        session = open_session(engine)

        # Get current active exchanges
        active_exchange_ids = aliased(Exchange, session.query(Exchange).filter(
            Exchange.active == 1).subquery())

        exchanges = session.query(active_exchange_ids).all()

        # Store the actual date
        today = date.today()

        # Show the timestamp on the JSON API
        graphs_dict = OrderedDict()
        graphs_dict['timestamp'] = datetime.now().strftime(
                                        "%a %b %d %Y, %H:%M:%S")

        # The following generates a Python dictionary storing BTC values
        # for the last 10 days obtained from active BTC exchanges
        for exchange in exchanges:
            values = []

            # Iterate on days from today to the last 10 days
            for i in range(1, 11):
                day = today + timedelta(days=-i)

                # Get the last currency value stored for current day
                query = session.query(Association).filter(
                    Association.date == day).filter(
                    Association.exchange_id == exchange.id).order_by(
                    Association.time.desc()).first()

                if query is None:
                    # If the script is getting null values for current day,
                    # then puts the last value obtained.
                    if day == today:
                        query = session.query(Association).filter(
                        Association.exchange_id == exchange.id).order_by(
                        Association.time.desc()).first()
                        values.append(query.last)
                    else:
                        values.append(None)
                else:
                    values.append(query.last)

            key_name = exchange.name.lower()
            graphs_dict[key_name] = values[::-1]

        # Generate JSON file from ordered dictionary
        json_path = output_dir + 'graphs.json'
        print 'Generating ' + json_path + ' file...'
        write_json_file(graphs_dict, json_path)

    except exc.SQLAlchemyError, exception:
        print 'Error %s:' % exception.args[0]
        sys.exit(1)

    finally:
        if session:
            session.close()


def generate_marketcap_json(output_dir):
    """
    Get marketcap values from coinmarketcap.com and output to a JSON file.
    :param output_dir: Output directory to write serialized JSON in filesystem.
    """
    try:
        # Get full web page from Coinmarketcap.com index.
        session = requests.Session()
        link = 'http://coinmarketcap.com/'
        req = session.get(link)

        # Create BeautifulSoup object with web response.
        soup = BeautifulSoup(req.text)

        # Ordered dictionary object to store data to be JSON serialized.
        marketcap_dict = OrderedDict()
        marketcap_dict['timestamp'] = datetime.now().strftime(
                                        '%a %b %d %Y, %H:%M:%S')
        marketcap_dict['currencies'] = []

        # Regex expression to search for patterns in web page.
        anything = re.compile('^.*$')
        name_regex = re.compile('^.*\\bcurrency-name\\b.*$')
        marketcap_regex = re.compile('^.*\\bmarket-cap\\b.*$')
        price_regex = re.compile('^.*\\bprice\\b.*$')
        positive_change_regex = re.compile('^.*\\bpositive_change\\b.*$')
        negative_change_regex = re.compile('^.*\\bnegative_change\\b.*$')

        # Find HTML <tr> tags for each currency.
        table = soup.findAll('tr', {'id': anything})

        # Find the top 5 (five) currencies with the highest marketcap
        # and obtain their values
        for item in table[:5]:
            currency = []

            # Get the currency name
            names = item.findAll('td', {'class': name_regex})
            for name in names:
                currency.append(name.find('a').contents[0].strip())

            # Get the marketcap value
            marketcaps = item.findAll('td', {'class': marketcap_regex})
            for marketcap in marketcaps:
                currency.append(marketcap.contents[0].strip())

            # Get the price value
            prices = item.findAll('a', {'class': price_regex})
            for price in prices:
                currency.append(price.contents[0].strip())

            # Get the change percentage and sign
            changes = item.findAll('td', {'class': positive_change_regex})

            if changes:
                for change in changes:
                    currency.append(change.contents[0].strip())
                    currency.append('positive')
            else:
                changes = item.findAll('td', {'class': negative_change_regex})
                for change in changes:
                    currency.append(change.contents[0].strip())
                    currency.append('negative')

            marketcap_dict['currencies'].append(currency)

        # Generate JSON file from ordered dictionary
        json_path = output_dir + 'marketcap.json'
        print 'Generating ' + json_path + ' file...'
        write_json_file(marketcap_dict, json_path)

    except Exception as exception:
        print 'Error %s:' % exception.args[0]
        send_email(
                    'daemon@bitcharts.org',
                    'staff@bitcharts.org',
                    'ERROR',
                    exception.args[0]
                    )


Base = declarative_base()


class Currency(Base):
    """
    SQLAlchemy ORM class to store information about currencies on database.
    """
    __tablename__ = "currencies"

    id = Column(Integer, Sequence('currency_id_seq'), primary_key=True)
    name = Column(String(10), unique=True)
    description = Column(String)
    cryptocurrency = Column(Boolean)
    active = Column(Boolean)

    def __init__(self, name, description, cryptocurrency, active):
        """Docstring"""
        self.name = name
        self.description = description
        self.cryptocurrency = cryptocurrency
        self.active = active


class Exchange(Base):
    """
    SQLAlchemy ORM class to store information about exchanges on database.
    """
    __tablename__ = "exchanges"

    id = Column(Integer, Sequence('exchange_id_seq'), primary_key=True)
    name = Column(String(10))
    country = Column(String(10))
    url = Column(String)
    api = Column(String)
    currency_id = Column(Integer, ForeignKey("currencies.id"))
    currency = relationship("Currency",
                            backref=backref("exchanges", order_by=id))
    active = Column(Boolean)

    def __init__(self, name, country, url, api, currency_id, active):
        """Docstring"""
        self.name = name
        self.country = country
        self.url = url
        self.api = api
        self.currency_id = currency_id
        self.active = active


class Association(Base):
    """
    SQLAlchemy ORM class to store current currencies' values obtained from
    APIs available on each exchange.
    """
    __tablename__ = 'exchanges_currencies'

    id = Column(Integer, Sequence('association_id_seq'), primary_key=True)
    exchange_id = Column(Integer, ForeignKey('exchanges.id'))
    currency_id = Column(Integer, ForeignKey('currencies.id'))
    last = Column(Float)
    date = Column(Date, default=date.today())
    time = Column(Time, default=datetime.now().time())

    def __init__(self, exchange_id, currency_id, last):
        self.exchange_id = exchange_id
        self.currency_id = currency_id
        self.last = last

    def asdict(self, session):
        """
        Function which returns an ordered dictionary containing field values
        from the current Association object.
        """
        properties = OrderedDict()

        id = self.exchange_id
        exchange = session.query(Exchange).filter(Exchange.id == id).first()
        properties['display_URL'] = exchange.url
        properties['display_name'] = exchange.name
        properties['currency'] = exchange.currency.name

        if exchange.currency.name == 'ARS':
            properties['blue'] = self.last
        else:
            properties['last'] = self.last

        return exchange.name.lower(), properties


def parse_args():
    """
    Options parser for running the Python script directly from shell to
    create and initialize Bitcharts database for the first time.
    """
    parser = argparse.ArgumentParser(prog='bitcharts.py')

    parser.add_argument("-d", "--database-name",
                        help="Name for new database to create",
                        dest="database_name")
    parser.add_argument("-c", "--currencies-file",
                        help="Configuration file with currencies information",
                        dest="currencies_file")
    parser.add_argument("-e", "--exchanges-file",
                        help="Configuration file with exchanges information",
                        dest="exchanges_file")

    if len(sys.argv) < 6:
        print '\nERROR: Too few arguments.\n'
        parser.print_help()
        sys.exit()

    args = parser.parse_args()

    if args.database_name and args.currencies_file and args.exchanges_file:
        # Append to filename a descriptive extension
        filename = args.database_name + '.sqlite'

        # If database file exists do not overwrite
        if os.path.exists(filename):
            print '\nERROR: Database file '" + filename + "' already exists.\n'
            sys.exit()

        # Compose the full database URL to be passed to db connection string
        database_url = 'sqlite:///' + filename

        # Create database schema based on the SQLAlchemy ORM
        create_tables(database_url)

        # Initialize database with values obtained from configuration files
        initialize_database(database_url,
                            args.currencies_file,
                            args.exchanges_file)
    else:
        print '\nERROR: You must specify valid inputs.\n'
        parser.print_help()
        sys.exit()


def main():
    """
    Main function.
    """
    try:
        parse_args()
    except KeyboardInterrupt:
        print 'Aborting... Interrupted by user.'
        sys.exit(0)

if __name__ == '__main__':
    main()
