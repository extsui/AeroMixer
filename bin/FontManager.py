#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy as np
import FontImage

class FontManager:
    def __init__(self, font4x8_file, font8x8_file):
        self.font4x8 = FontImage.FontImage(font4x8_file, 4, 8, 16, 4)
        self.font8x8 = FontImage.FontImage(font8x8_file, 8, 8, 94, 8)

    def str_to_bitmap(self, sjis_str, raw=False):
        bitmap = []
        ch_array = np.fromstring(sjis_str, dtype=np.uint8)
        i = 0
        while i < len(ch_array):
            if self.sjis_is_multi(ch_array[i]):
                ch_x, ch_y = self.sjis_multi_to_ch_xy(ch_array[i], ch_array[i+1])
                ch_data = self.font8x8.get(ch_x, ch_y)
                i += 2
            else:
                ch_x, ch_y = self.sjis_ascii_to_ch_xy(ch_array[i])
                ch_data = self.font4x8.get(ch_x, ch_y)
                i += 1
            if raw is True:
                bitmap.extend(ch_data)
            else:
                bitmap.append(ch_data)
        return bitmap

    def sjis_is_multi(self, c):
        if (((c >= 0x81) and (c <= 0x9f)) or
            ((c >= 0xe0) and (c <= 0xef))):
            return True
        else:
            return False

    def sjis_ascii_to_ch_xy(self, c):
        ch_x = c % 16
        ch_y = c / 16
        return ch_x, ch_y

    def sjis_multi_to_ch_xy(self, hi, lo):
        """
        第一バイト
        ・[0x81～0x9f]と[0xe0～0xef]の範囲に大別される．
        ・前半であれば，0x81を引くだけでよい．
        ・後半であれば，0x81と2範囲の空間分を引く．
        ・" * 2" は第一バイトに2つの区(01～63)が含まれて
        　いることに対応させる計算である．
        """
        if 0x81 <= hi and hi <= 0x9f:
            ch_y = (hi - 0x81) * 2
        elif 0xe0 <= hi and hi <= 0xef:
            ch_y = (hi - 0x81 - (0xe0 - 0x9f - 1)) * 2

        """
        第二バイト
        ・[0x40～0x7e]と[0x80～0xfc]の範囲からなる．
        　見方を変えれば，0x7fのみが抜けた連番である．
        ・前半であれば，0x40を引くだけでよい．
        ・後半であれば，0x40と1(0x7fの分)を引く．
        """
        if 0x40 <= lo and lo <= 0x7e:
            ch_x = lo - 0x40
        elif 0x80 <= lo and lo <= 0xfc:
            ch_x = lo - 0x40 - 1

        return ch_x, ch_y
