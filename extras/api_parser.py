# -*- coding: utf-8 -*-

import json
from collections import OrderedDict

from bitcharts.utils import request_ticker


def get_ticker_LaNacion():
    """"""
    ticker_url = 'http://contenidos.lanacion.com.ar/json/dolar'
    blue_key = 'InformalCompraValue'
    oficial_key = 'CasaCambioCompraValue'

    res = OrderedDict()

    req = request_ticker(ticker_url)
    content = req.content[19:-2]
    data = json.loads(content)

    if (blue_key and oficial_key) in data:
        res['blue'] = float(data.get(blue_key).replace(',', '.'))
        res['oficial'] = float(data.get(oficial_key).replace(',', '.'))

    return json.dumps(res, sort_keys=False, indent=4)


def get_ticker_Infobae():
    """"""
    ticker_url = 'http://www.infobae.com/adjuntos/servicios/cotizacion.json'
    blue_key = u'dólar blue'
    oficial_key = u'dólar oficial'

    res = OrderedDict()

    req = request_ticker(ticker_url)
    content = req.content[1:-1]
    data = json.loads(content)

    if (blue_key and oficial_key) in data:
        b = data.get(blue_key)
        o = data.get(oficial_key)
        if isinstance(b, dict):
            res['blue'] = float(b['compra']['precio'].replace(',', '.'))
            res['oficial'] = float(o['compra']['precio'].replace(',', '.'))

    return json.dumps(res, sort_keys=False, indent=4)


def get_ticker_BitcoinBrothers():
    """"""
    ticker_url = 'https://bitcoinbrothers.co/sys/live'
    key = u'btc'

    res = OrderedDict()

    req = request_ticker(ticker_url, verify=False)
    content = req.content
    data = json.loads(content)

    if key in data:
        l = data.get(key)
        if isinstance(l, dict):
            res['last'] = float(l['buy_usd'])

    return json.dumps(res, sort_keys=False, indent=4)
