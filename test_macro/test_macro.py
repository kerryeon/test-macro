import asyncio
import operator
import os
import subprocess
from functools import reduce
from shutil import copyfile

import yaml
from tqdm import tqdm

from recorder import Recorder
from test_parser import TestParser


class MacroCase:

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
                return False
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
            return round(value, 6)
        return value

    def _flush(self):
        pass

    def __row__(self):
        return self._cases.keys()

    def __len__(self):
        return reduce(operator.mul, [1] + [len(v) for v in self._cases.values()])


class MacroFile(MacroCase):

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

    def _flush(self):
        raise NotImplementedError()

    def __row__(self):
        return [f'{self._filename}/{row}' for row in super().__row__()]



class MacroYAML(MacroFile):

    def __init__(self, lock, filename: str, dump=True):
        super().__init__(lock, filename, dump)
        with open(self.dumped or self._filename, 'r') as f:
            lines = f.readlines()[1:]
            self._data = yaml.load('\n'.join(lines), Loader=yaml.SafeLoader)

    def _flush(self):
        with open(self._filename, 'w') as f:
            f.write('%YAML:1.0\n')
            f.write(yaml.dump(self._data, Dumper=yaml.SafeDumper))


class TestMacro:

    def __init__(self):
        self._lock = False
        self._exes = []
        self._files = []
        self._for = []
        self._file_templates = [
            (MacroYAML, ('yaml', 'yml', )),
        ]
        self._for_templates = {
            'record': Recorder.fromCase,
        }
        self._exit_code = 0

    @property
    def exitCode(self):
        return self._exit_code

    def load(self, filename: str):
        try:
            data = MacroYAML(self._lock, filename, dump=False)._data
        except FileNotFoundError as e:
            print(e)
            self._exit(1)
            return False
        parser = TestParser()
        if 'files' in data.keys():
            for f in data['files']:
                filename, cases = next(iter(f.items()))
                f = self.addFile(filename)
                for values in cases:
                    key, values = next(iter(values.items()))
                    f.addCase(key, parser.parse(values))
        if 'for' in data.keys():
            for f in data['for']:
                command, args = next(iter(f.items()))
                if not isinstance(args, list) and not isinstance(args, dict):
                    args = [args]
                self._for.append((self._for_templates[command], args))
        if 'exes' in data.keys():
            for cmd in data['exes']:
                self.addExec(cmd)
        return True
                

    def addFile(self, filename: str, filetype: str = None):
        assert not self._lock, 'Appending while computing is not allowed'
        filetype = (filetype or filename.split('.')[-1]).lower()
        for cls, cases in self._file_templates:
            if filetype in cases:
                file = cls(self._check_lock, filename)
                self._files.append(file)
                return file
        raise NotImplementedError(f'Unsupported format: {filetype}')

    def addFor(self, function, args):
        self._for.append((function, args))

    def addExec(self, command: str):
        # TODO arguments
        self._exes.append(command)

    def addFileTemplate(self, cls: MacroCase, *cases):
        self._file_templates.append(cls, cases)

    def addForTemplate(self, command: str, builder):
        self._for_templates[command] = builder

    def _check_lock(self):
        return self._lock

    def _init(self):
        for f in self._files:
            f._init()

    def _step(self):
        for f in self._files:
            if not f._step():
                return False
        return True

    def _dump(self):
        return reduce(operator.add, [f._dump() for f in self._files])

    async def iterate(self):
        self._lock = True
        self._init()

        row = self.__row__()
        # TODO simplification
        if len(self._files) == 1:
            row = [r.split('.')[-1] for r in row]
        row = [r[-10:] for r in row]
        print(('{:>12s}' * len(row)).format(*row))

        # TODO more pretty
        with tqdm(total=len(self)) as pbar:
            while True:
                case = self._dump() 
                pbar.set_description(''.join(
                    '{:>12s}'.format(c[1][-10:]) if isinstance(c[1], str)
                    else '{:>12g}'.format(c[1])
                    for c in case
                ))
                # for
                for _fun, _args in self._for:
                    await _fun(case)(*_args)
                # exec
                for _cmd in self._exes:
                    await self._execute(_cmd)
                yield case
                await asyncio.sleep(0.1)
                pbar.update()
                if self._step():
                    break
        self._lock = False

    async def _execute(self, command: str):
        process = subprocess.Popen(command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL)
        while True:
            retcode = process.poll()
            if retcode is not None:
                break
            else:
                await asyncio.sleep(0.01)
                continue
        # (output, err) = process.communicate()
        exit_code = process.wait()
        if exit_code != 0:
            self._exit(exit_code)

    def _exit(self, exit_code: int):
        self._lock = False
        self._exit_code = int(exit_code)
        asyncio.get_event_loop().stop()

    def __row__(self):
        return reduce(operator.add, [f.__row__() for f in self._files])

    def __len__(self):
        return reduce(operator.mul, [len(f) for f in self._files])
