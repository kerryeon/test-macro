import asyncio
import os
from datetime import datetime

import cv2
import mss
import numpy as np
import Xlib
from ewmh import EWMH


class Recorder:

    ID = {}
    QUEUE = {}

    def __init__(self, output: str, fps: float = 30.0):
        self._ewmh = EWMH()
        self._sct = None
        self._geometry = self._ewmh.getDesktopGeometry()
        self._writer = None
        self._output = output
        self._delay = 1.0 / fps
        self._fps = fps

        self._width = 0
        self._height = 0

        if not os.path.exists('recorded'):
            os.mkdir('recorded')

    async def record(self, wm_name: str):
        await self.__class__.wait(wm_name)
        asyncio.ensure_future(self._record(wm_name))

    @classmethod
    def fromCase(cls, case):
        return Recorder(cls.naming(case)).record

    @classmethod
    async def wait(cls, wm_name: str):
        # ID
        if wm_name not in cls.ID.keys():
            cls.ID[wm_name] = max([0, *cls.ID.values()])
        _id = cls.ID[wm_name]
        # wait by ID
        while (_id in cls.QUEUE.keys()) or (_id > len(cls.QUEUE)):
            await asyncio.sleep(0.1)
        cls.QUEUE[wm_name] = {
            'top': 0,
            'left': 0,
            'width': 0,
            'height': 0,
        }

    @classmethod
    async def signal(cls, wm_name: str):
        del cls.QUEUE[wm_name]

    @classmethod
    def naming(cls, case):
        def _shorten(name):
            # int
            if isinstance(name, float) and name % 1 == 0:
                return str(int(name))
            # maybe path
            if isinstance(name, str):
                return name.split('/')[-1]
            return str(name)
        return '_'.join(reversed([_shorten(c[1]) for c in case]))

    async def _record(self, wm_name: str):
        begin, tick = datetime.now(), 0
        tracking = False
        await asyncio.sleep(1)
        while True:
            ts_last = datetime.now()
            # retrieve
            try:
                frames = [w for w in self._ewmh.getClientList() if wm_name in (w.get_wm_name() or '')]
                if len(frames) != 1:
                    if len(frames) > 1:
                        print(
                            '-' * 36 + '\n' +
                            f'!  {len(frames)} windows have been captured.\n' +
                            '.\n'.join(f'| {self._ewmh.getWmName(w).decode()}' for w in frames) +
                            '\n' + ('-' * 36)
                        )
                        break
                    if tracking:
                        break
                    await asyncio.sleep(self._delay / 2)
                    continue
                # the only frame
                bbox = self._get_frame(frames[0]).get_geometry()
                monitor = {'top': bbox.y, 'left': bbox.x, 'width': bbox.width, 'height': bbox.height}
            except Xlib.error.BadWindow:
                continue
            # move window
            if not tracking:
                tracking = True
                monitor = self._update_window(wm_name, monitor, frames[0])
                self._sct = mss.mss()
            if bbox.x + bbox.width > self._geometry[0]:
                monitor['width'] = self._geometry[0] - bbox.x
            if bbox.y + bbox.height > self._geometry[1]:
                monitor['height'] = self._geometry[1] - bbox.y
            img = np.array(self._sct.grab(monitor))
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
            self._write(img, wm_name)
            # end
            tick += 1
            ts = datetime.now()
            await asyncio.sleep(max(0, self._delay * (tick - (ts - begin).total_seconds() * self._fps) * 0.9))
        # flush
        self.__close__()
        await self.__class__.signal(wm_name)

    def _write(self, img, wm_name):
        height, width = img.shape[:2]
        if self._writer is None or self._width != width or self._height != height:
            fourcc = cv2.VideoWriter_fourcc(*'FMP4')
            self._writer = cv2.VideoWriter(
                f'recorded/{self._output}-{"_".join(wm_name.lower().split(" "))}.avi',
                fourcc, self._fps, (width, height), False)
            self._width, self._height = width, height
        self._writer.write(img)

    def _get_frame(self, client):
        frame = client
        while frame.query_tree().parent != self._ewmh.root:
            frame = frame.query_tree().parent
        return frame

    def _update_window(self, wm_name, monitor, frame):
        width = sum(m['width'] for m in self.__class__.QUEUE.values())
        monitor['left'] = width
        monitor['top'] = 0
        if frame.get_wm_class() is None:
            w, h = monitor['width'], monitor['height']
        else:
            w, h = 0, None
        # TODO 2-d replacement
        self.__class__.QUEUE[wm_name] = monitor
        self._ewmh.setMoveResizeWindow(
            frame, x=monitor['left'], y=monitor['top'], w=w, h=h)
        self._ewmh.display.flush()
        return monitor

    def __close__(self):
        if hasattr(self, '_writer') and self._writer is not None:
            self._writer.release()
            self._writer = None
        if hasattr(self, '_sct') and self._sct is not None:
            self._sct.close()
            self._sct = None

    def __del__(self):
        self.__close__()
