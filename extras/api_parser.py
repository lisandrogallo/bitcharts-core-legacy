# -*- coding: utf-8 -*-

from bitcharts.utils import request_ticker
from collections import OrderedDict
import json


def get_ticker_LaNacion():
    """"""
    res = OrderedDict()
    blue_key = 'InformalCompraValue'
    oficial_key = 'CasaCambioCompraValue'

    req = request_ticker(
        'http://contenidos.lanacion.com.ar/json/dolar'
    )

    content = req.content[19:-2]

    data = json.loads(content)

    if (blue_key and oficial_key) in data:
        res['blue'] = float(data.get(blue_key).replace(',', '.'))
        res['oficial'] = float(data.get(oficial_key).replace(',', '.'))

    return json.dumps(res, sort_keys=False, indent=4)


def get_ticker_Infobae():
    """"""
    res = OrderedDict()
    blue_key = u'dólar blue'
    oficial_key = u'dólar oficial'

    req = request_ticker(
        'http://www.infobae.com/adjuntos/servicios/cotizacion.json'
    )

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
    res = OrderedDict()
    key = u'btc'

    req = request_ticker(
        'https://bitcoinbrothers.co/sys/live', verify=False
    )

    content = req.content

    data = json.loads(content)

    if key in data:
        l = data.get(key)
        if isinstance(l, dict):
            res['last'] = float(l['buy_usd'])

    return json.dumps(res, sort_keys=False, indent=4)
