#!/usr/bin/python
# -*- coding: utf-8 -*-
import MP3FileManager as MP3
import STFTAudio as STFT

import exceptions

stft = STFT.STFTAudio()
mp3 = MP3.MP3FileManager()

mp3.download_list()
mp3.sort(MP3.MP3FileManager.SORT_BY_NAME)

while True:
    while True:
        print('[' + mp3.get() + ']')
        s = raw_input('(+|-|s|q)> ')
        if s == '+':
            mp3.next()
        elif s == '-':
            mp3.prev()
        elif s == 's':
            break
        elif s == 'q':
            raise exceptions.NotImplementedError('quit')

    print('select: ' + mp3.get())
    mp3.download_file()

    stft.open(mp3.to_wave())

    print('playing...')
    stft.start()

    while stft.is_playing() or stft.is_stopping():
        s = raw_input('(s|p|f)> ')
        if s == 's':
            stft.start()
        elif s == 'p':
            stft.stop()
        elif s == 'f':
            print stft.stft()

    stft.close()
    mp3.rm_wave()
