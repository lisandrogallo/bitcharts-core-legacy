# -*- coding: utf-8 -*-

from ConfigParser import SafeConfigParser

from requests import get, post


class MyParser(SafeConfigParser):
    def as_dict(self):
        d = dict(self._sections)
        for k in d:
            d[k] = dict(self._defaults, **d[k])
            d[k].pop('__name__', None)
        return d


def request_ticker(api_url, verify=True):

    resp = post(api_url, verify=verify) or get(api_url, verify=verify)

    if 200 != resp.status_code:
        return False

    return resp


def get_ticker(api_url):
    try:
        req = request_ticker(api_url)
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
            if not isinstance(data.get(key), dict):
                return float(data.get(key))
        else:
            for v in data.itervalues():
                search = search_key(v, key)
                if search:
                    return search
    elif isinstance(data, list):
        return search_key(data[0], key)
    return False


def write_file(content, path):
    """
    Write content to filesystem.
    :param content: Anything printable.
    :param path: Fullpath to write file in filesystem.
    """
    with open(path, 'w') as f:
        print >> f, content
    f.close()
