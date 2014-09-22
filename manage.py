# -*- coding: utf-8 -*-

from flask.ext.script import Manager
from bitcharts.database import manager as database_manager
from bitcharts.api_parser import get_ticker, search_key
from bitcharts import app, db, Exchange, Currency, Association
from sys import exit


# @app.errorhandler(DatabaseError)
# def special_exception_handler(error):
#     return 'Database connection failed', 500

manager = Manager(app, with_default_commands=False)

manager.add_command('database', database_manager)


@manager.command
def get_values():
    """"""
    # api_url = 'http://www.bitstamp.net/api/ticker/'
    api_url = 'https://btc-e.com/api/2/btc_usd/ticker'
    key = 'last'
    req_json = get_ticker(api_url)
    if req_json:
        # print 'Bitstamp: %s' % search_key(req_json, key)
        print 'BTC-e: %s' % search_key(req_json, key)

    active_exchanges = Exchange.query.filter_by(active=True)

    active_currencies = [
        x.id for x in Currency.query.filter_by(active=True).all()
    ]

    active_exchanges_currencies = active_exchanges.filter(
        Exchange.currency_id.in_(active_currencies)
    ).all()

    print active_exchanges_currencies

if __name__ == "__main__":
    manager.run()
