import os

import numpy as np
from lark import Lark, Transformer
from lark.exceptions import UnexpectedCharacters


_syntax = r'''
start           : expr

expr            : term ((OP_ADD | OP_SUB) term)*
term            : seq ((OP_MUL | OP_DIV) seq)*
seq             : (power OP_SEQ)* power
power           : (atom OP_POW)* atom

OP_ADD          : "+"
OP_SUB          : "-"
OP_MUL          : "*"
OP_DIV          : "/"

OP_SEQ          : "--"
OP_POW          : "**"

range           : "(" expr "," expr [","] ")"

atom            : number
                | range

number          : DEC_NUMBER | HEX_NUMBER | BIN_NUMBER | OCT_NUMBER | FLOAT_NUMBER | IMAG_NUMBER

DEC_NUMBER      : /([-+]?)(0|[1-9]\d*)/i
HEX_NUMBER.2    : /0x[\da-f]*/i
OCT_NUMBER.2    : /0o[0-7]*/i
BIN_NUMBER.2    : /0b[0-1]*/i
FLOAT_NUMBER.2  : /((\d+\.\d+)(e[-+]?\d+)?|\d+(e[-+]?\d+))/i
IMAG_NUMBER.2   : /\d+j/i | FLOAT_NUMBER "j"i

%ignore /[\t \f\n]+/  // WS

'''


class Range:

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __seq__(self, other):
        interval = (self.end - self.start) / (int(other) - 1)
        interval = round(interval, 6)
        return np.arange(self.start, self.end + 1e-8, interval)

    def __add__(self, other):
        self.start += other
        self.end += other
        return self

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other):
        self.start *= other
        self.end *= other
        return self

    def __truediv__(self, other):
        return self * (1 / other)

    def __radd__(self, other):
        return other + self.__arange__()

    # def __rsub__(self, other):
    #     raise NotImplementedError()  # TODO

    def __rmul__(self, other):
        return other * self.__arange__()

    # def __rtruediv__(self, other):
    #     raise NotImplementedError()  # TODO

    def __rpow__(self, other):
        return other ** self.__arange__()

    def __arange__(self):
        return np.arange(int(self.start), int(self.end) + 1)


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
    def _calc(cls, args):
        if len(args) == 1:
            return args[0]
        value = args[0]
        for op, other in zip(args[1::2], args[2::2]):
            value = cls.MAP[str(op)](value, other)
        return value


class TestParser:

    def __init__(self):
        self._p = Lark(_syntax, parser='lalr')

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
