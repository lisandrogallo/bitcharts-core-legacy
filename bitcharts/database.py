# -*- coding: utf-8 -*-

from flask.ext.script import Manager, prompt_bool
from bitcharts.utils import MyParser
from bitcharts import app, db


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
    print config_parser(exchanges_file)
    print config_parser(currencies_file)


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
