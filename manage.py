# -*- coding: utf-8 -*-

from flask.ext.script import Manager
from bitcharts import app, db
from bitcharts.utils import MyParser

manager = Manager(app, with_default_commands=False)
exchanges = app.config.get('EXCHANGES_FILE', False)
currencies = app.config.get('CURRENCIES_FILE', False)


def config_parser(config_file):
    f = MyParser()
    f.read(config_file)
    return f.as_dict()


@manager.command
def create_db(exchanges_file=exchanges, currencies_file=currencies):
    """Docstring"""
    db.create_all()
    print config_parser(exchanges_file)
    print config_parser(currencies_file)


if __name__ == "__main__":
    manager.run()
