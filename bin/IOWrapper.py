#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import exceptions
import UsbDevice

class IOWrapper:
    INPUT_NEXT   = '+'
    INPUT_PREV   = '-'
    INPUT_SELECT = 's'
    INPUT_QUIT   = 'q'

    def __init__(self, usb=False):
        """ 出力先をUSBか標準出力にするかを設定 """
        if usb is False:
            self.dev = None
        else:
            self.dev = UsbDevice.UsbDevice(0x0000, 0x0000)

    def read(self, timeout=None):
        """ 1文字入力(改行は削除) """
        import select
        rlist, _, _ = select.select([sys.stdin], [], [], timeout)
        if rlist:
            return sys.stdin.readline().strip()
        else:
            return None

    def input(self, timeout=None):
        if self.dev is None:
            return self.read(timeout)
        else:
            raise exceptions.NotImplementedError
    
    def output_music_name(self, music_name):
        # TODO: USBの場合，SJISへの変換が必要
        if self.dev is None:
            """
            標準出力の場合，明示的に曲名を保存して
            output_spectrum()時に表示する．
            USBの場合，マイコンで曲名を保存しておく．
            """
            self.music_name = music_name
            print(music_name)
        else:
            raise exceptions.NotImplementedError

    def output_spectrum(self, spec):
        if self.dev is None:
            """
            (1) 画面をクリア
            (2) 左上に曲名を表示
            (3) スペクトルを表示
            """
            import os
            os.system('clear')
            self.output_music_name(self.music_name)
            for y in range(32)[::-1]:
                for x in spec:
                    if x > y:
                        sys.stdout.write('___ ')
                    else:
                        sys.stdout.write('    ')
                sys.stdout.write('\n')
        else:
            raise exceptions.NotImplementedError
