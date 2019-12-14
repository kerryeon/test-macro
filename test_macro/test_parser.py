import os

import numpy as np
from lark import Lark, Transformer
from lark.exceptions import UnexpectedCharacters


class Range:

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __seq__(self, other):
        interval = (self.end - self.start) / (int(other) - 1)
        return np.arange(self.start, self.end + interval, interval)

    def __add__(self, other):
        self.start += other
        self.end = other
        return self

    def __mul__(self, other):
        self.start *= other
        self.end *= other
        return self

    def __radd__(self, other):
        return other + self.__arange__()

    def __rmul__(self, other):
        return other * self.__arange__()

    def __rpow__(self, other):
        return other ** self.__arange__()

    def __arange__(self):
        return np.arange(int(self.start), int(self.end) + 1)

    def __str__(self):
        return f'({self.start}, {self.end})'

    def __repr__(self):
        return str(self)


class EvalExpressions(Transformer):

    def number(self, args):
        return float(args[0])

    def atom(self, args):
        return args[0]

    def range(self, args):
        return Range(*args)

    def power(self, args):
        return self._calc(args)

    def seq(self, args):
        return self._calc(args)

    def term(self, args):
        return self._calc(args)

    def expr(self, args):
        return self._calc(args)

    def start(self, args):
        return args[0]

    MAP = {
        '+': lambda x, y: x + y,
        '-': lambda x, y: x - y,
        '*': lambda x, y: x * y,
        '/': lambda x, y: x / y,
        '--': lambda x, y: x.__seq__(y),
        '**': lambda x, y: x ** y,
    }

    @classmethod
    def _calc(cls, args, reversed: bool = False):
        if len(args) == 1:
            return args[0]
        if reversed:
            args = reversed(args)
        value = args[0]
        for op, other in zip(args[1::2], args[2::2]):
            value = cls.MAP[str(op)](value, other)
        return value


class TestParser:

    def __init__(self, path: str = None):
        path = path or f'{os.path.dirname(__file__)}/test_parser.lark'
        with open(path) as f:
            self._p = Lark(f.read(), parser='lalr')

    def parse(self, q):
        if isinstance(q, list):
            # list
            return np.concatenate([self.parse(_q) for _q in q], axis=0)
        if isinstance(q, float) or isinstance(q, int):
            # atom
            return np.array([q])
        try:
            # expr
            t = self._p.parse(q)
        except UnexpectedCharacters:
            # string
            return np.array([q])
        q = EvalExpressions().transform(t)
        if isinstance(q, Range):
            return q.__arange__()
        return q
