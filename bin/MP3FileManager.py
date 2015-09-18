#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import random
from collections import deque

class MP3FileManager:
    __TOKEN_PATH    = '../token_store.txt'
    __DOWNLOAD_PATH = '../download/'

    SORT_BY_NAME   = 0
    SORT_BY_RANDOM = 1

    def __init__(self):
        self.__mp3_list = None
        self.__is_connected = False

    def download_list(self):
        # ネットワークに接続できる場合
        # file_list = ...
        # ネットワークに接続できない場合
        file_list = os.listdir(self.__DOWNLOAD_PATH)

        mp3_list = filter(lambda f: f.endswith('.mp3'), file_list)
        self.__mp3_list = deque(mp3_list)

    def sort(self, order):
        if order == self.SORT_BY_NAME:
            sorted_list = list(self.__mp3_list)
            sorted_list.sort()
            self.__mp3_list = deque(sorted_list)
        elif order == self.SORT_BY_RANDOM:
            random.shuffle(self.__mp3_list)

    def get(self):
        return self.__mp3_list[0]

    def next(self):
        self.__mp3_list.rotate(1)

    def prev(self):
        self.__mp3_list.rotate(-1)

    def download_file(self):
        dst_path = self.__DOWNLOAD_PATH + self.get()
        print('download_file: ' + self.get())
        print('dst_path: ' + dst_path)
        # TODO: ファイルが存在しない場合ダウンロード
        # ...
        return dst_path

    def to_wav(self):
        # TODO: *.mp3 --> *.wav
        pass

if __name__ == '__main__':
    mp3 = MP3FileManager()
    mp3.download_list()
    print(mp3._MP3FileManager__mp3_list)
    mp3.sort(MP3FileManager.SORT_BY_RANDOM)
    print(mp3._MP3FileManager__mp3_list)
    mp3.sort(MP3FileManager.SORT_BY_NAME)
    print(mp3._MP3FileManager__mp3_list)
    print(mp3.get())
    mp3.next()
    print(mp3.get())
    mp3.prev()
    print(mp3.get())
    mp3.download_file()
