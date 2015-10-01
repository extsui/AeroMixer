#!/usr/bin/python
# -*- coding: utf-8 -*-
import MP3FileManager as MP3
import STFTAudio as STFT
import IOWrapper as IO

import sys
import exceptions

STATE_INIT    = 0
STATE_SELECT  = 1
STATE_PREPARE = 2
STATE_PLAY    = 3
STATE_STOP    = 4
STATE_FINISH  = 5
STATE_QUIT    = 6

state = STATE_INIT

print('AeroMixer: start')

""" '--usb'を指定した場合，出力先をUSBに変更(通常は標準出力) """
argv = sys.argv
argc = len(argv)
if argc == 2 and argv[1] == '--usb':
    usb = True
else:
    usb = False
    print('AeroMixer: no-usb')
io = IO.IOWrapper(usb)

while True:

    if state == STATE_INIT:
        stft = STFT.STFTAudio()
        mp3 = MP3.MP3FileManager()
        mp3.download_list()
        mp3.sort(MP3.MP3FileManager.SORT_BY_NAME)
        state = STATE_SELECT

    elif state == STATE_SELECT:
        io.output_music_name(mp3.get())
        s = io.input()
        if s == IO.IOWrapper.INPUT_NEXT:
            mp3.next()
        elif s == IO.IOWrapper.INPUT_PREV:
            mp3.prev()
        elif s == IO.IOWrapper.INPUT_SELECT:
            state = STATE_PREPARE
        elif s == IO.IOWrapper.INPUT_QUIT:
            state = STATE_QUIT

    elif state == STATE_PREPARE:
        mp3.download_file()
        stft.open(mp3.to_wave())
        stft.start()
        state = STATE_PLAY

    elif state == STATE_PLAY:
        if not stft.is_playing():
            state = STATE_FINISH
        s = io.input(timeout=STFT.STFTAudio.STFT_INTERVAL)
        if s is None:
            io.output_spectrum(stft.stft())
        elif s == IO.IOWrapper.INPUT_SELECT:
            stft.stop()
            state = STATE_STOP
        elif s == IO.IOWrapper.INPUT_QUIT:
            state = STATE_QUIT

    elif state == STATE_STOP:
        s = io.input()
        if s == IO.IOWrapper.INPUT_SELECT:
            stft.start()
            state = STATE_PLAY
        elif s == IO.IOWrapper.INPUT_QUIT:
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
