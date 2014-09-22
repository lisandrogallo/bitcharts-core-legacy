# -*- coding: utf-8 -*-

from flask.ext.script import Manager, prompt_bool
from bitcharts.utils import MyParser
from bitcharts import app, db, Exchange, Currency
from ast import literal_eval


manager = Manager(usage='Perform database operations')
exchanges = app.config.get('EXCHANGES_FILE', False)
currencies = app.config.get('CURRENCIES_FILE', False)


def config_parser(config_file):
    f = MyParser()
    f.read(config_file)
    return f.as_dict()


@manager.command
def create(exchanges_file=exchanges, currencies_file=currencies):
    """Creates database schema from SQLAlchemy models"""

    db.create_all()

    currencies = config_parser(currencies_file)

    for key, value in currencies.iteritems():
        # TO-DO: add exception handling for incorrect values in config files
        currency = Currency(
            name=key,
            description=value['description'],
            cryptocurrency=literal_eval(value['cryptocurrency']),
            active=literal_eval(value['active'])
        )

        db.session.add(currency)

    db.session.commit()

    exchanges = config_parser(exchanges_file)

    for key, value in exchanges.iteritems():
        # TO-DO: add exception handling for incorrect values in config files
        currency = Currency.query.filter_by(name=value['currency']).first()
        exchange = Exchange(
            name=key,
            country=value['country'],
            url=value['url'],
            api=value['api'],
            key=value['key'],
            currency_id=currency.id,
            active=literal_eval(value['active'])
        )

        db.session.add(exchange)

    db.session.commit()


@manager.command
def rebuild():
    "Recreates database tables"
    if prompt_bool('Are you sure you want to rebuild database?'):
        db.drop_all()
        create()


# @manager.command
# def drop():
#     """Drops database tables"""
#     if prompt_bool('Are you sure you want to erase all data?'):
#         db.drop_all()


# @manager.command
# def create(default_data=True, sample_data=False):
#     """Creates database schema from SQLAlchemy models"""
#     db.create_all()
#     populate(default_data, sample_data)


# @manager.command
# def rebuild(default_data=True, sample_data=False):
#     "Recreates database tables (same as issuing 'drop' and then 'create')"
#     drop()
#     create(default_data, sample_data)


# @manager.command
# def populate(default_data=False, sample_data=False):
#     "Populate database with default data"
#     from fixtures import dbfixture

#     if default_data:
#         from fixtures.default_data import all
#         default_data = dbfixture.data(*all)
#         default_data.setup()

#     if sample_data:
#         from fixtures.sample_data import all
#         sample_data = dbfixture.data(*all)
#         sample_data.setup()
