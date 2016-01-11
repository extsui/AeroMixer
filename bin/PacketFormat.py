#!/usr/bin/python
# -*- coding: utf-8 -*-

""" OUT(ホストからデバイス)のパケット """
"""
(1) 制御パケット(2バイト)
  [0] ID_CONTROL
  [1] 各種制御情報
"""
ID_CONTROL  = 0
CONTROL_BITMAP_CLEAR   = 0x1
CONTROL_DISPLAY_ENABLE = 0x2
CONTROL_SCROLL_ENABLE  = 0x4
CONTROL_SHUTDOWN       = 0x8

"""
(2) ビットマップパケット(5バイト)
  [0] ID_BITMAP
  [1-5] 縦8横4のビットマップデータ
"""
ID_BITMAP   = 1
BITMAP_SIZE = 4

"""
(3) スペクトルパケット(33バイト)
  [0] ID_SPECTRUM
  [1-33] スペクトルデータ
"""
ID_SPECTRUM = 2
SPECTRUM_SIZE = 32

""" IN(デバイスからホスト)のパケット """
"""
入力パケット(1バイト)
  [0] 入力情報

  *INは1種類しかないためID無し
"""
INPUT_NEXT   = 0x1
INPUT_PREV   = 0x2
INPUT_SELECT = 0x4
INPUT_QUIT   = 0x8
