#!/usr/bin/python
# -*- coding: utf-8 -*-
import random

class ListManager:
    SORT_BY_NAME   = 0
    SORT_BY_RANDOM = 1

    def __init__(self, init_list):
        random.seed()
        self.list = list(init_list)
        self.pos = 0
        self.len = len(self.list)

    def get(self):
        return dict({'pos' : self.pos + 1,
                     'len' : self.len,
                     'name': self.list[self.pos]})

    def next(self):
        self.pos = (self.pos + 1) % self.len

    def prev(self):
        self.pos = (self.pos - 1) % self.len

    def sort(self, order):
        if order == self.SORT_BY_NAME:
            self.list.sort()
        elif order == self.SORT_BY_RANDOM:
            random.shuffle(self.list)
