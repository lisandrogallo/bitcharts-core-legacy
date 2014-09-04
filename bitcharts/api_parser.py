#-*- coding: utf-8 -*-

from requests import post


def get_ticker(api_url):
    try:
        req = post(api_url)
        json_data = req.json()
        return json_data
    except:
        return False


def search_key(data, key):
    if isinstance(data, dict):
        if key in data:
            return float(data.get(key))
        else:
            for v in data.itervalues():
                return search_key(v, key)
    return False
