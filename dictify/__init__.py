import re
import math


class Field:
    def __init__(self):
        self.queries = []
        self.value = None

    def verify(func):
        def wrapper(self, *args, **kw):
            def _():
                func(self, *args, **kw)
            self.queries.append(_)
            return self
        return wrapper

    def _verify(self, key, value):
        self.key = key
        self.value = value
        for query in self.queries:
            try:
                query()
            except ValueError as e:
                raise ValueError("'%s' : %s" % (self.key, e.args[0]))
        return self.value

    @verify
    def required(self):
        if (self.value is None) or (self.value == ''):
            raise ValueError('required')

    @verify
    def default(self, default):
        if self.value is None:
            self.value = default

    @verify
    def type(self, classinfo):
        if not(isinstance(self.value, classinfo)):
            raise ValueError('must be %s object' % classinfo)

    @verify
    def match(self, re_):
        if not re.match(re_, self.value):
            raise ValueError("value not match with '%s'" % re_)

    @verify
    def apply(self, func):
        func(self)

    @verify
    def size(self, min=0, max=math.inf):
        if not (min <= len(self.value) <= max):
            raise ValueError("len(%s) be %s to %s" % (self.key, min, max))


class Dictify(dict):
    def __new__(cls, dict_):
        cls._field = dict()
        for k, v in vars(cls).items():
            if isinstance(v, Field):
                cls._field[k] = v
                dict_[k] = v._verify(k, dict_.get(k))
        return super().__new__(cls, dict_)

    def __setitem__(self, k, v):
        v = self._field[k]._verify(k, v)
        return super().__setitem__(k, v)
