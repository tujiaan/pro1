import functools

import parse
from flask import request
from flask_restplus import reqparse

range_parser = reqparse.RequestParser()
range_parser.add_argument('from', type=int, help='开始', required=False, location='args')
range_parser.add_argument('count', type=int, help='数量', required=False, location='args')


class Range(object):
    start = None
    offset = None

    def __init__(self, string):
        if string is not None:
            a = parse.search("items={start:d}-{offset:d}", string)
            b = parse.search("items={start:d}-", string)
            c = parse.search("items=-{offset:d}", string)
            s = a or b or c
            if s:
                s = s.named
                self.start = s.get('start', None)
                self.offset = s.get('offset', None)


def page_range(s=0, o=None):
    def decorator(method):
        @functools.wraps(method)
        def warpper(*args, **kwargs):
            result = (method(*args, **kwargs))
            code = None
            header = {}
            if isinstance(result, tuple):
                l = len(result)
                code = result[1] if l > 1 else None
                header = result[2] if l > 2 else {}
                result = result[0]
            r = Range(request.headers.get('Range'))
            r2 = range_parser.parse_args()
            start = r.start or r2.get('from') or s
            offset = r.offset or r2.get('count') or o
            totle = result.count()
            if offset is  None:
                offset=totle-start
            result = result.offset(start).limit(offset)
            header['Content-Range'] = f'items {start}-{start+offset if start+offset<totle else totle}/{totle}'
            return result.all(), code, header

        return warpper

    return decorator
