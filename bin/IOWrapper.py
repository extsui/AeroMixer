#!/usr/bin/python
# -*- coding: utf-8 -*-
import exceptions
import UsbDevice
import socket
import ScreenThread
import threading
import numpy as np

class IOWrapper:
    INPUT_NEXT   = '+'
    INPUT_PREV   = '-'
    INPUT_SELECT = 's'
    INPUT_QUIT   = 'q'

    def __init__(self, usb=False):
        """ 出力先をUSBか標準出力にするかを設定 """
        """ 具体的な処理の違いはopen()以降 """
        self.usb = usb

    def open(self):
        if self.usb is False:
            self.dev = None
            self.host_so, dev_so = \
                socket.socketpair(socket.AF_UNIX, socket.SOCK_DGRAM, 0)
            self.kill_event = threading.Event()
            self.kill_event.clear()
            """ ScreenThreadは非同期動作であり，ソケットを通して通信 """
            self.screen = ScreenThread.ScreenThread(dev_so, self.kill_event)
            self.screen.start()
        else:
            self.dev = UsbDevice.UsbDevice(0x0000, 0x0000)

    def close(self):
        if self.dev is None:
            self.kill_event.set()
            self.screen.join()
        else:
            pass

    def input(self, timeout=None):
        if self.dev is None:
            self.host_so.settimeout(timeout)
            try:
                in_data = self.host_so.recv(1)
            except:
                in_data = None
            return in_data
        else:
            raise exceptions.NotImplementedError
    
    def output_music_name(self, music_name):
        pass

    def output_spectrum(self, spec):
        if self.dev is None:
            self.host_so.settimeout(None)
            send_data = np.array(spec, dtype=np.uint8)
            self.host_so.send(send_data)
        else:
            raise exceptions.NotImplementedError
