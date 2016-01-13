#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# 以下のコマンドでインストールすること
# % sudo pip install pyalsaaudio 
#
import alsaaudio

""" 音量を操作するクラス """
class VolumeController:

    def __init__(self):
        self.mixer = alsaaudio.Mixer('PCM')

    def plus(self, num):
        """ R/Lの音量は同じと仮定して一方のみの音量を使用 """
        volume = self.mixer.getvolume()[0]
        new_volume = volume + num
        """ 指定可能な範囲は[0:100] """
        if new_volume < 0:
            new_volume = 0
        elif new_volume > 100:
            new_volume = 100
        self.mixer.setvolume(new_volume)
