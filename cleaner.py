#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Bitcharts Database Cleaner
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

from bitcharts import clean_database
import argparse
import sys

def parse_args():
    """
    Options parser for running the Python script daemon directly from shell.
    """
    parser = argparse.ArgumentParser(prog='Bitcharts database cleaner')

    parser.add_argument('-d', '--database-name',
                        dest='database_name')
    parser.add_argument('-n', '--number-days',
                        help='Number of days to keep',
                        action='store')

    if len(sys.argv) < 5:
        print '\nERROR: Too few arguments.\n'
        parser.print_help()
        sys.exit()

    args = parser.parse_args()

    if args.database_name and args.number_days:
        database_url = 'sqlite:///' + args.database_name
        clean_database(database_url, args.number_days)
    else:
        print '\nERROR: You must specify valid inputs.\n'
        parser.print_help()
        sys.exit()

def main():
    """Main function."""
    try:
        parse_args()
    except KeyboardInterrupt:
        print 'Aborting... Interrupted by user.'
        sys.exit(0)


if __name__ == '__main__':
    main()
