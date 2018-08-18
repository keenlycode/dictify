import re
import math


class Field:
    def __init__(self):
        self.queries = []

    def query(func):
        def wrapper(self, *args, **kw):
            def _():
                func(self, *args, **kw)
            self.queries.append(_)
            return self
        return wrapper

    def _query(self, key, value):
        self.key = key
        self.value = value
        for query in self.queries:
            try:
                query()
            except ValueError as e:
                raise ValueError("'%s' : %s" % (self.key, e.args[0]))
        return self.value

    @query
    def match(self, re_):
        if not re.match(re_, self.value):
            raise ValueError("value not match with '%s'" % re_)

    @query
    def size(self, min=0, max=math.inf):
            if not (min <= len(self.value) <= max):
                raise ValueError("len(%s) be %s to %s" % (self.key, min, max))

    @query
    def required(self):
        if self.value is None:
            raise ValueError('required')

    @query
    def default(self, default):
        if self.value is None:
            self.value = default


class Model(dict):
    def __new__(cls, dict_):
        cls._field = dict()
        for k, v in vars(cls).items():
            if isinstance(v, Field):
                cls._field[k] = v
                dict_[k] = v._query(k, dict_.get(k))
        return super().__new__(cls, dict_)
