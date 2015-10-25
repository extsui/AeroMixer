#!/usr/bin/python
# -*- coding: utf-8 -*-
import exceptions
import UsbDevice
import socket
import ScreenThread
import threading
import numpy as np
import FontManager as font

"""
ホストtoデバイスパケットは以下の3種類
(1) 制御パケット
(2) ビットマップパケット
(3) スペクトルパケット
"""
ID_CONTROL  = 0
BITMAP_CLEAR   = 0x1
DISPLAY_ENABLE = 0x2
SCROLL_ENABLE  = 0x4
ID_BITMAP   = 1
ID_SPECTRUM = 2

class IOWrapper:
    INPUT_NEXT   = '+'
    INPUT_PREV   = '-'
    INPUT_SELECT = 's'
    INPUT_QUIT   = 'q'

    def __init__(self, usb=False):
        """ 出力先をUSBか標準出力にするかを設定 """
        """ 具体的な処理の違いはopen()以降 """
        self.usb = usb
        """ 文字列をフォントに変換する """
        self.font = font.FontManager('../font/misaki_4x8_jisx0201.fnt',
                                     '../font/misaki_gothic.fnt')

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

    """
    曲名文字列(UTF-8)
    ---> SJIS文字列
    ---> ビットマップ配列
    ---> ビットマップ配列を8バイト長に切り上げ(0埋め)
    ---> 8バイト毎にビットマップパケットを構築して送信
    """
    def output_music_name(self, music_name):
        """ encode('shift-jis')だとエラーになる """
        sjis_str = music_name.encode('cp932')
        bitmap = self.font.str_to_bitmap(sjis_str, raw=True)

        send_data = [ID_CONTROL]
        send_data.append(BITMAP_CLEAR)
        send_data = np.array(send_data, dtype=np.uint8)
        self.host_so.send(send_data)

        i = 0
        while True:
            send_data = [ID_BITMAP]
            data = bitmap[i*8:(i+1)*8]
            send_data.extend(data)
            if len(data) is 0:
                break
            elif (0 < len(data) and len(data) < 8):
                addnum = 8 - len(data)
                for j in range(addnum):
                    send_data.append(0)
                break
            send_data = np.array(send_data, dtype=np.uint8)
            self.host_so.send(send_data)
            i += 1

        send_data = [ID_CONTROL]
        send_data.append(DISPLAY_ENABLE | SCROLL_ENABLE)
        send_data = np.array(send_data, dtype=np.uint8)
        self.host_so.send(send_data)

    def output_spectrum(self, spec):
        if self.dev is None:
            self.host_so.settimeout(None)
            send_data = [ID_SPECTRUM]
            send_data.extend(spec)
            send_data = np.array(send_data, dtype=np.uint8)
            self.host_so.send(send_data)
        else:
            raise exceptions.NotImplementedError
