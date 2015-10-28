#!/usr/bin/python
# -*- coding: utf-8 -*-

""" OUT(ホストからデバイス)のパケット """

""" (1) 制御パケット """
ID_CONTROL  = 0
CONTROL_BITMAP_CLEAR   = 0x1
CONTROL_DISPLAY_ENABLE = 0x2
CONTROL_SCROLL_ENABLE  = 0x4

""" (2) ビットマップパケット """
ID_BITMAP   = 1
BITMAP_SIZE = 4

""" (3) スペクトルパケット """
ID_SPECTRUM = 2
SPECTRUM_SIZE = 32
