# -*- coding: utf-8 -*-

from bitcharts.utils import request_ticker
import json


def get_ticker_LaNacion():
    """"""
    key = 'InformalCompraValue'
    req = request_ticker('http://contenidos.lanacion.com.ar/json/dolar')

    content = req.content[19:-2]

    data = json.loads(content)

    if key in data:
        last = data.get(key)
        res = {
            'last': float(last.replace(',', '.'))
        }

    print res


def get_ticker_Infobae():
    """"""

    key = u'dólar blue'
    req = request_ticker(
        'http://www.infobae.com/adjuntos/servicios/cotizacion.json'
    )

    content = req.content[1:-1]

    data = json.loads(content)

    if key in data:
        j = data.get(key)
        if isinstance(j, dict):
            last = j['compra']['precio']
            res = {
                'last': float(last.replace(',', '.'))
            }

        print res
