import abc
import os
from shutil import copyfile

from .case import MacroCase


class MacroFile(MacroCase, metaclass=abc.ABCMeta):

    def __init__(self, lock, filename: str, dump=True):
        super().__init__(lock)
        self._is_dump = dump
        self._filename = filename
        # backup
        if self._is_dump and not os.path.exists(self.dumped):
            copyfile(self._filename, self.dumped)

    @property
    def dumped(self):
        return f'{self._filename}.bak' if self._is_dump else None

    def __row__(self):
        return [f'{self._filename}/{row}' for row in super().__row__()]
