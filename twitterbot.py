#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Bitcharts Twitter Bot
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

from tweepy import OAuthHandler, API
from bitcharts import get_last_from_exchange
import argparse
import sys
import os


# Complete with the corresponding information from your Twitter application:
CONSUMER_KEY = ''
CONSUMER_SECRET = ''
ACCESS_KEY = ''
ACCESS_SECRET = ''


def tweet_this(exchange_name, last_value, dolar_blue):
    """
    Make a tweet with last currency value for the given exchange name.
    :param exchange_name: Exchange name.
    :param last_value: Last currency value.
    :param dolar_blue: Last dolar blue value.
    """

    # Connect to Twitter API service
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = API(auth)

    # Convert last currency value in USD to ARS
    value_ars = last_value * dolar_blue

    # Full message to tweet
    btc_ars_str = '1 BTC = $'+ format(value_ars, ',.2f') + ' ARS '
    source_str = '· Source: #' + exchange_name
    dolar_str = ' | Dolar: ' + str(dolar_blue)
    suffix_str = ' #bitcoin #Argentina · More info: http://bitcharts.io'
    tweet = btc_ars_str + source_str + dolar_str + suffix_str

    # Tweet it!
    api.update_status(tweet)

def parse_args():
    """
    Options parser for running the Python script directly from shell.
    """
    parser = argparse.ArgumentParser(prog='Bitcharts JSON Generator')

    parser.add_argument('-d', '--database_name',
                        dest='database_name',
                        action='store',
                        required=True)
    parser.add_argument('-e', '--exchange-name',
                        dest='exchange_name',
                        action='store',
                        choices=['Bitstamp', 'BitcoinAverage', 'BTC-e'],
                        required=True)

    args = parser.parse_args()

    if not os.path.exists(args.database_name):
        print '\nERROR: Database file ' + args.database_name + ' does not exist.\n'
        sys.exit()

    database_url = 'sqlite:///' + args.database_name

    last_value = get_last_from_exchange(database_url, args.exchange_name)


    if last_value:
        dolar_blue = get_last_from_exchange(database_url, 'Geeklab')
        if dolar_blue:
            exchange_name = args.exchange_name.replace('-', '')
            tweet_this(exchange_name, last_value, dolar_blue)

def main():
    """Main function."""
    try:
        parse_args()
    except KeyboardInterrupt:
        print 'Aborting... Interrupted by user.'
        sys.exit(0)


if __name__ == '__main__':
    main()
