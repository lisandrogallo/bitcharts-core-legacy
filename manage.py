# -*- coding: utf-8 -*-

from flask.ext.script import Manager
from bitcharts.database import manager as database_manager
from bitcharts.api_parser import get_ticker, search_key
from bitcharts import app


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


if __name__ == "__main__":
    manager.run()
