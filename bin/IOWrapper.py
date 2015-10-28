#!/usr/bin/python
# -*- coding: utf-8 -*-
import exceptions
import UsbDevice
import socket
import ScreenThread
import threading
import numpy as np
import FontManager as font
import PacketFormat as PF

class IOWrapper:
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
                data = self.host_so.recv(1)
                in_data = ord(data)
            except:
                in_data = None
            return in_data
        else:
            raise exceptions.NotImplementedError

    def output_control(self, bitmap_clear=False,
                       display_enable=False,
                       scroll_enable=False):
        send_data = [PF.ID_CONTROL]
        cmd = 0
        if bitmap_clear:
            cmd |= PF.CONTROL_BITMAP_CLEAR
        if display_enable:
            cmd |= PF.CONTROL_DISPLAY_ENABLE
        if scroll_enable:
            cmd |= PF.CONTROL_SCROLL_ENABLE
        send_data.append(cmd)
        send_data = np.array(send_data, dtype=np.uint8)
        self.host_so.send(send_data)

    """
    曲名文字列(UTF-8)
    ---> SJIS文字列
    ---> ビットマップ配列
    ---> ビットマップ配列を4バイト毎に区切って送信
         (半角文字が最小4バイトであるため)
    ---> 4バイト毎にビットマップパケットを構築して送信
    """
    def output_string(self, unicode_str):
        """ encode('shift-jis')だとエラーになる """
        sjis_str = unicode_str.encode('cp932')
        bitmap = self.font.str_to_bitmap(sjis_str, raw=True)

        for i in range(0, len(bitmap), PF.BITMAP_SIZE):
            send_data = [PF.ID_BITMAP]
            send_data.extend(bitmap[i:i+PF.BITMAP_SIZE])
            send_data = np.array(send_data, dtype=np.uint8)
            self.host_so.send(send_data)

    def output_spectrum(self, spec):
        if self.dev is None:
            self.host_so.settimeout(None)
            send_data = [PF.ID_SPECTRUM]
            send_data.extend(spec)
            send_data = np.array(send_data, dtype=np.uint8)
            self.host_so.send(send_data)
        else:
            raise exceptions.NotImplementedError
