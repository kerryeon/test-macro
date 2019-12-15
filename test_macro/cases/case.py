import abc
import operator
from functools import reduce


class MacroCase(metaclass=abc.ABCMeta):

    def __init__(self, lock):
        self._lock = lock
        self._cases = {}
        self._ptr = None

    def addCase(self, key: str, values):
        assert not self._lock(), 'Appending while computing is not allowed'
        assert len(values) > 0, 'More than 0 cases are needed'
        self._cases[key] = values

    def _init(self):
        self._ptr = [0] * len(self._cases)
        for key, values in self._cases.items():
            self._update(key, values[0])
        self._flush()

    def _step(self):
        if len(self._cases) == 0:
            return True
        for i, (key, values) in enumerate(self._cases.items()):
            self._ptr[i] += 1
            if self._ptr[i] >= len(values):
                self._ptr[i] = 0
                self._update(key, values[self._ptr[i]])
            else:
                self._update(key, values[self._ptr[i]])
                self._flush()
                return False
        self._flush()
        return True

    def _update(self, key: str, value):
        # TODO node
        value = value.item()
        # rounding
        self._data[key] = self._format(key, value)

    def _dump(self):
        return [(key, self._format(key, values[i])) for i, (key, values) in zip(self._ptr, self._cases.items())]

    def _format(self, key, value):
        if key in self._data.keys():
            _type = type(self._data[key])
            value = _type(value)
        if isinstance(value, float):
            value = round(value, 6)
        return value

    @abc.abstractmethod
    def _flush(self):
        pass

    def __row__(self):
        return self._cases.keys()

    def __len__(self):
        return reduce(operator.mul, [1] + [len(v) for v in self._cases.values()])
