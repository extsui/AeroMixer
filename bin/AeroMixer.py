#!/usr/bin/python
# -*- coding: utf-8 -*-
import MP3FileManager as MP3
import STFTAudio as STFT

import sys
import exceptions

def read_timeout(timeout):
    from select import select
    rlist, _, _ = select([sys.stdin], [], [], timeout)
    if rlist:
        return sys.stdin.readline().strip()
    else:
        return None

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
        s = read_timeout(timeout=0.100)
        if stft.is_playing() and s is None:
            print(stft.stft())
        elif s == 's':
            stft.start()
        elif s == 'p':
            stft.stop()

    stft.close()
    mp3.rm_wave()
