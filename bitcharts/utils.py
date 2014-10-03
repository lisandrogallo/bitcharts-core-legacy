# -*- coding: utf-8 -*-

from ConfigParser import SafeConfigParser
from requests import post, get


class MyParser(SafeConfigParser):
    def as_dict(self):
        d = dict(self._sections)
        for k in d:
            d[k] = dict(self._defaults, **d[k])
            d[k].pop('__name__', None)
        return d


def get_ticker(api_url):
    try:
        req = post(api_url) or get(api_url)
        if req:
            print req
            json_data = req.json()
            return json_data
        else:
            return False
    except:
        return False


def search_key(data, key):
    print type(data)
    if isinstance(data, dict):
        if key in data:
            return float(data.get(key))
        else:
            for v in data.itervalues():
                search = search_key(v, key)
                if search:
                    return search
    elif isinstance(data, list):
        return search_key(data[0], key)
    return False
