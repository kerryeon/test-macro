import asyncio

import pytest
from test_macro import TestMacro
from test_macro.macro import main as _main


@pytest.mark.asyncio
async def test_not_loaded():
    macro = TestMacro()
    assert not macro.load('hello.ghost.yml')


@pytest.mark.asyncio
async def test_unsupported_format():
    macro = TestMacro()
    try:
        macro.load('test_supported_format.yml')
        assert False
    except NotImplementedError:
        pass


@pytest.mark.asyncio
async def test_no_cases():
    macro = TestMacro()
    assert macro.load('test_no_cases.yml')
    async for _ in macro.iterate():
        pass
    assert macro.exitCode == 0


@pytest.mark.asyncio
async def test_one_case():
    macro = TestMacro()
    assert macro.load('test_one_case.yml')
    async for _ in macro.iterate():
        pass
    assert macro.exitCode == 0


@pytest.mark.asyncio
async def test_exe_not_exists():
    macro = TestMacro()
    assert macro.load('test_exe_not_exists.yml')
    async for _ in macro.iterate():
        pass
    assert macro.exitCode != 0


@pytest.mark.asyncio
async def test_main():
    pass  # TODO
