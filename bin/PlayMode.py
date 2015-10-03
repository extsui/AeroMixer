#!/usr/bin/python
# -*- coding: utf-8 -*-
from collections import deque

class PlayMode:
    MODE_SINGLE     = 'single'
    MODE_CONTINUOUS = 'continuous'
    MODE_RANDOM     = 'random'

    def __init__(self):
        self.mode_list = deque([self.MODE_SINGLE,
                                self.MODE_CONTINUOUS,
                                self.MODE_RANDOM])

    def get(self):
        return self.mode_list[0]

    def next(self):
        self.mode_list.rotate(-1)

    def prev(self):
        self.mode_list.rotate(1)
