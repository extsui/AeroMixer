#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy as np

class FontImage:
    def __init__(self, fontfile, ch_width, ch_height,
                 ch_num_in_line, ch_byte_size):
        self.font = np.fromfile(fontfile, dtype=np.uint8)
        self.ch_width = ch_width
        self.ch_height = ch_height
        self.ch_num_in_line = ch_num_in_line
        self.ch_byte_size = ch_byte_size

    def ch_to_index(self, ch_x, ch_y):
        return (ch_y * self.ch_num_in_line + ch_x) * self.ch_byte_size

    def get(self, ch_x, ch_y):
        index = self.ch_to_index(ch_x, ch_y)
        ch_data = []
        for i in range(self.ch_byte_size):
            ch_data.append(self.font[index + i])
        return ch_data
