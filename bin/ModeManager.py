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
