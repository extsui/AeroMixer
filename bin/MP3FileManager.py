#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import ListManager as LM
import DropboxDownloader
from urllib3.exceptions import MaxRetryError

import subprocess

class MP3FileManager(LM.ListManager):
    __TOKEN_PATH    = '../token_store.txt'
    __DOWNLOAD_PATH = '../download/'
    __TMP_PATH      = '../tmp/'

    def __init__(self):
        self.__is_connected = False
        self.dbd = DropboxDownloader.DropboxDownloader(self.__TOKEN_PATH)
        self.mp3_list = LM.ListManager.__init__(self, self.__download_list())

    def __download_list(self):
        try:
            file_list = self.dbd.do_ls()
            print('--- Network mode ---')
            self.__is_connected = True
        except MaxRetryError:
            file_list = os.listdir(self.__DOWNLOAD_PATH)
            print('--- Local mode ---')
            self.__is_connected = False
        return filter(lambda f: f.endswith('.mp3'), file_list)

    def download_file(self):
        from_path = self.get()['name']
        to_path = self.__DOWNLOAD_PATH + from_path
        #print('download_file: ' + to_path)
        if not os.path.isfile(to_path):
            if self.__is_connected:
                self.dbd.do_get(from_path, to_path)
            else:
                print('BUG')

    def to_wave(self):
        """  ../download/xxx.mp3 --> ../tmp/xxx.wav """
        mp3_path = self.__DOWNLOAD_PATH + self.get()['name']
        wave_path = self.__TMP_PATH + os.path.basename(mp3_path).replace('.mp3', '.wav')
        # TODO: waveファイルが存在した場合失敗する
        subprocess.check_call(['ffmpeg', '-i', mp3_path,
                               '-ac', '1', '-ar', '44100', wave_path],
                              stderr=-1)
        return wave_path

    def rm_wave(self):
        wave_path = self.__TMP_PATH + os.path.basename(self.get()['name']).replace('.mp3', '.wav')
        if os.path.isfile(wave_path):
            os.unlink(wave_path)

    # DEBUG
    def play_wave(self):
        wave_path = self.__TMP_PATH + self.get()['name'].replace('.mp3', '.wav')
        subprocess.call(['aplay', '-q', wave_path])

if __name__ == '__main__':
    mp3 = MP3FileManager()
    mp3.sort(MP3FileManager.SORT_BY_RANDOM)
    mp3.sort(MP3FileManager.SORT_BY_NAME)
    print(mp3.get()['name'])
    mp3.next()
    print(mp3.get()['name'])
    mp3.prev()

    print('download:' + mp3.get()['name'])
    mp3.download_file()

    wave_path = mp3.to_wave()
    print('converted:' + wave_path)

    print('playing...')
    mp3.play_wave()

    print('unlink')
    mp3.rm_wave()
