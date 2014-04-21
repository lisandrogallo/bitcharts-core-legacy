#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Bitcharts JSON Generator
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

from bitcharts import write_values
from bitcharts import generate_sources_json, generate_graphs_json
from bitcharts import generate_marketcap_json
import argparse
import sys


def parse_args():
    """
    Options parser for running the Python script directly from shell.
    """
    parser = argparse.ArgumentParser(prog='Bitcharts JSON Generator')

    parser.add_argument('-d', '--database-name',
                        dest='database_name',
                        action='store',
                        required=True),
    parser.add_argument('-o', '--output-dir',
                        dest='output_dir',
                        action='store',
                        required=True),
    parser.add_argument('-s', '--sources-json',
                        action='store_true',
                        required=False),
    parser.add_argument('-g', '--graphs-json',
                        action='store_true',
                        required=False),
    parser.add_argument('-m', '--marketcap-json',
                        action='store_true',
                        required=False)

    args = parser.parse_args()

    database_url = 'sqlite:///' + args.database_name

    if args.sources_json:
        write_values(database_url)
        generate_sources_json(database_url, args.output_dir)

    if args.graphs_json:
        generate_graphs_json(database_url, args.output_dir)

    if args.marketcap_json:
        generate_marketcap_json(args.output_dir)


def main():
    """Main function."""
    try:
        parse_args()
    except KeyboardInterrupt:
        print 'Aborting... Interrupted by user.'
        sys.exit(0)


if __name__ == '__main__':
    main()
