#!/usr/bin/python
# -*- coding: utf-8 -*-
import MP3FileManager as MP3
import STFTAudio as STFT

import sys
import exceptions

def read_timeout(timeout=None):
    from select import select
    rlist, _, _ = select([sys.stdin], [], [], timeout)
    if rlist:
        return sys.stdin.readline().strip()
    else:
        return None

STATE_INIT    = 0
STATE_SELECT  = 1
STATE_PREPARE = 2
STATE_PLAY    = 3
STATE_STOP    = 4
STATE_FINISH  = 5
STATE_QUIT    = 6

state = STATE_INIT

print('AeroMixer: start')

while True:

    if state == STATE_INIT:
        stft = STFT.STFTAudio()
        mp3 = MP3.MP3FileManager()
        mp3.download_list()
        mp3.sort(MP3.MP3FileManager.SORT_BY_NAME)
        state = STATE_SELECT

    elif state == STATE_SELECT:
        print('[' + mp3.get() + ']')
        sys.stderr.write('(+|-|s|q)> ')
        s = read_timeout()
        if s == '+':
            mp3.next()
        elif s == '-':
            mp3.prev()
        elif s == 's':
            state = STATE_PREPARE
        elif s == 'q':
            state = STATE_QUIT

    elif state == STATE_PREPARE:
        print('download')
        mp3.download_file()
        print('convert')
        stft.open(mp3.to_wave())
        print('play')
        stft.start()
        state = STATE_PLAY

    elif state == STATE_PLAY:
        if not stft.is_playing():
            state = STATE_FINISH
        s = read_timeout(timeout=0.050)
        if s is None:
            spec = stft.stft()
            import os
            os.system('clear')
            for y in range(32)[::-1]:
                for x in spec:
                    if x > y:
                        sys.stdout.write('___ ')
                    else:
                        sys.stdout.write('    ')
                sys.stdout.write('\n')
        elif s == 's':
            stft.stop()
            state = STATE_STOP
        elif s == 'q':
            state = STATE_QUIT

    elif state == STATE_STOP:
        s = read_timeout()
        if s == 's':
            stft.start()
            state = STATE_PLAY
        elif s == 'q':
            state = STATE_QUIT

    elif state == STATE_FINISH:
        stft.close()
        mp3.rm_wave()
        state = STATE_SELECT

    elif state == STATE_QUIT:
        # STOPからQUITになった場合，tmp/にwavファイルが残るけど，
        # アンマウント時に削除されるので問題ない．
        break

    else:
        raise exceptions.SystemError('STATE ERROR')

print('AeroMixer: exit')
