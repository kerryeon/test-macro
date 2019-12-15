import asyncio

import pytest
from test_macro import TestMacro


@pytest.mark.asyncio
async def test_parser():
    macro = TestMacro()
    assert macro.load('test_parser.yml')
    async for a in macro.iterate():
        pass
    assert macro.exitCode == 0
