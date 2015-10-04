#!/usr/bin/python
# -*- coding: utf-8 -*-
import ListManager as LM

class ModeManager(LM.ListManager):
    MODE_SINGLE     = 'single'
    MODE_CONTINUOUS = 'continuous'
    MODE_RANDOM     = 'random'

    def __init__(self):
        mode_list = [self.MODE_SINGLE,
                     self.MODE_CONTINUOUS,
                     self.MODE_RANDOM]
        LM.ListManager.__init__(self, mode_list)

    def is_require_name_sort(self):
        name = self.get()['name']
        return (name is self.MODE_SINGLE or
                name is self.MODE_CONTINUOUS)

    def is_require_random_sort(self):
        name = self.get()['name']
        return name is self.MODE_RANDOM

    def is_auto_mode(self):
        name = self.get()['name']
        return (name is self.MODE_CONTINUOUS or
                name is self.MODE_RANDOM)
