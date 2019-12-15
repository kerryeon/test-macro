import argparse
import asyncio

from tqdm import tqdm

from .recorder import Recorder
from .test_macro import TestMacro


async def _test(macro, loop, filepath: str):
    if macro.load(filepath):
        async for _ in macro.iterate():
            pass
    loop.stop()


def main():
    parser = argparse.ArgumentParser(description='Simple fully automatic macro.')
    parser.add_argument('-p', metavar='PATH', type=str, default='case.yml',
                        help='a yaml file containing test cases')
    args = parser.parse_args()

    macro = TestMacro()

    loop = asyncio.get_event_loop()
    asyncio.ensure_future(main(macro, loop, args.p))
    loop.run_forever()

    exit(macro.exitCode)


if __name__ == '__main__':
    main()
