#!/usr/bin/python
# -*- coding: utf-8 -*-
import MP3FileManager as MP3
import STFTAudio as STFT
import IOWrapper as IO
import ModeManager as MM
import VolumeController as VC

import sys
import exceptions

import logging
logger = logging.getLogger('AeroMixer')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('../AeroMixer.log')
formatter = logging.Formatter('[%(asctime)s] %(module)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

STATE_INIT    = 0
STATE_MODE    = 1
STATE_SELECT  = 2
STATE_PREPARE = 3
STATE_PLAY    = 4
STATE_STOP    = 5
STATE_FINISH  = 6
STATE_QUIT    = 7

state = STATE_INIT

logger.debug('start')

""" '--usb'を指定した場合，出力先をUSBに変更(通常は標準出力) """
argv = sys.argv
argc = len(argv)
if argc == 2 and argv[1] == '--usb':
    usb = True
else:
    usb = False
io = IO.IOWrapper(usb)

while True:

    if state == STATE_INIT:
        stft = STFT.STFTAudio()
        mp3 = MP3.MP3FileManager()
        mode = MM.ModeManager()
        vol = VC.VolumeController()
        io.open()
        state = STATE_MODE

    elif state == STATE_MODE:
        cur_mode = mode.get()
        io.output_control(bitmap_clear=True, display_enable=False, scroll_enable=False)
        io.output_string('[%d/%d] %s' % (cur_mode['pos'], cur_mode['len'], cur_mode['name']))
        io.output_control(bitmap_clear=False, display_enable=True, scroll_enable=False)
        s = io.input()
        if s == IO.IOWrapper.INPUT_NEXT:
            mode.next()
        elif s == IO.IOWrapper.INPUT_PREV:
            mode.prev()
        elif s == IO.IOWrapper.INPUT_SELECT:
            if mode.is_require_name_sort() is True:
                mp3.sort(MP3.MP3FileManager.SORT_BY_NAME)
            elif mode.is_require_random_sort() is True:
                mp3.sort(MP3.MP3FileManager.SORT_BY_RANDOM)
            state = STATE_SELECT
        elif s == IO.IOWrapper.INPUT_QUIT:
            state = STATE_QUIT

    elif state == STATE_SELECT:
        cur_music = mp3.get()
        io.output_control(bitmap_clear=True, display_enable=False, scroll_enable=False)
        io.output_string(u'[%d/%d] %s' % (cur_music['pos'], cur_music['len'], cur_music['name'].strip(u'.mp3')))
        io.output_control(bitmap_clear=False, display_enable=True, scroll_enable=False)
        """
        単曲再生: 選曲
        連続再生/ランダム再生: スキップ
        """
        if mode.is_auto_mode() is True:
            state = STATE_PREPARE
        else:
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
        io.output_control(bitmap_clear=True, display_enable=False, scroll_enable=False)
        io.output_string(u'◆Ｎｏｗ Ｄｏｗｎｌｏａｄｉｎｇ')
        io.output_control(bitmap_clear=False, display_enable=True, scroll_enable=False)
        mp3.download_file()

        io.output_control(bitmap_clear=True, display_enable=False, scroll_enable=False)
        io.output_string(u'◆Ｎｏｗ Ｃｏｎｖｅｒｔｉｎｇ')
        io.output_control(bitmap_clear=False, display_enable=True, scroll_enable=False)
        stft.open(mp3.to_wave())

        io.output_control(bitmap_clear=True, display_enable=False, scroll_enable=False)
        io.output_string(u'♪' + mp3.get()['name'].strip(u'.mp3'))
        io.output_control(bitmap_clear=False, display_enable=True, scroll_enable=True)
        stft.start()
        state = STATE_PLAY

    elif state == STATE_PLAY:
        if not stft.is_playing():
            state = STATE_FINISH
        s = io.input(timeout=STFT.STFTAudio.STFT_INTERVAL)
        if s is None:
            io.output_spectrum(stft.stft())
        elif s == IO.IOWrapper.INPUT_NEXT:
            vol.plus(5)
        elif s == IO.IOWrapper.INPUT_PREV:
            vol.plus(-5)
        elif s == IO.IOWrapper.INPUT_SELECT:
            stft.stop()
            io.output_control(bitmap_clear=False, display_enable=True, scroll_enable=False)
            state = STATE_STOP
        elif s == IO.IOWrapper.INPUT_QUIT:
            state = STATE_QUIT

    elif state == STATE_STOP:
        s = io.input()
        if s == IO.IOWrapper.INPUT_SELECT:
            stft.start()
            io.output_control(bitmap_clear=False, display_enable=True, scroll_enable=True)
            state = STATE_PLAY
        elif s == IO.IOWrapper.INPUT_QUIT:
            state = STATE_QUIT

    elif state == STATE_FINISH:
        stft.close()
        mp3.rm_wave()
        mp3.next()
        state = STATE_SELECT

    elif state == STATE_QUIT:
        """ ScreenThreadの終了処理実行(usbの場合は何もしない) """
        io.close()
        # STOPからQUITになった場合，tmp/にwavファイルが残るけど，
        # アンマウント時に削除されるので問題ない．
        break

    else:
        raise exceptions.SystemError('STATE ERROR')

logger.debug('exit')
