import os
from unittest.mock import patch

from test_macro.cases import MacroCase, MacroFile


def test_case():
    p = patch.multiple(MacroCase, __abstractmethods__=set())
    p.start()
    cases = MacroCase(lambda: False)
    cases._flush()
    p.stop()


def test_file():
    filename = 'dummy_proc_void.yml'
    filename_bak = f'{filename}.bak'
    if os.path.exists(filename_bak):
        os.remove(filename_bak)

    p = patch.multiple(MacroFile, __abstractmethods__=set())
    p.start()
    cases = MacroFile(lambda: False, filename)
    p.stop()
