#!/usr/bin/python
# -*- coding: utf-8 -*-
import threading
import curses
import FontManager
import numpy as np
import PacketFormat as PF

WIN_WIDTH = 256
WIN_HEIGHT = 32

POLLING_SEC = 0.050
SCROLL_SEC = POLLING_SEC * 1.5

class ScreenThread(threading.Thread):
    def __init__(self, dev_so):
        """
        ・ホストと通信するためのソケット
        ・タイムアウト有りのブロッキング動作
        """
        self.dev_so = dev_so
        self.dev_so.setblocking(1)
        self.dev_so.settimeout(POLLING_SEC)
        """ 画面表示制御 """
        self.bitmap = [0]
        self.is_display_enable = False
        self.is_scroll_enable = False
        self.rest_scroll_sec = 0
        self.base_x = 0
        super(ScreenThread, self).__init__()

    def run(self):
        curses.wrapper(self.curses_main)

    def curses_main(self, stdscr):
        """ エコーバックOFF，バッファリングOFF，カーソルOFF """
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)

        """ 
        ・新規ウィンドウを作成
        ・表示タイミングをdoupdate()時に設定
        ・getch()を非ブロッキング動作に設定
        """
        self.win = curses.newwin(WIN_HEIGHT, WIN_WIDTH)
        self.win.noutrefresh()
        self.win.timeout(0)

        while True:
            if self.main_loop() is False:
                break

    def main_loop(self):
        """ 入力の有無を確認し，あればホストに送信 """
        c = self.win.getch()
        if c is not curses.ERR:
            if 0 <= c and c <= 255:
                c = chr(c)
                data = 0
                if c == '+':
                    data |= PF.INPUT_NEXT
                if c == '-':
                    data |= PF.INPUT_PREV
                if c == 's':
                    data |= PF.INPUT_SELECT
                if c == 'q':
                    data |= PF.INPUT_QUIT
                send_data = np.array(data, dtype=np.uint8)
                self.dev_so.send(send_data)

        """ 受信に成功したら対応する処理を実行し，タイムアウト時はnop """
        try:
            recv_data = self.dev_so.recv(64)
            data = np.fromstring(recv_data, dtype=np.uint8)
            if data[0] == PF.ID_CONTROL:
                cmd = data[1]
                if cmd & PF.CONTROL_SHUTDOWN:
                    return False
                if cmd & PF.CONTROL_BITMAP_CLEAR:
                    self.bitmap = [0 for i in xrange(WIN_WIDTH)]
                    self.draw_bitmap(0, 0)
                    self.bitmap = []
                    self.base_x = 0
                self.is_display_enable = True if cmd & PF.CONTROL_DISPLAY_ENABLE else False
                self.is_scroll_enable = True if cmd & PF.CONTROL_SCROLL_ENABLE else False
            elif data[0] == PF.ID_BITMAP:
                self.bitmap.extend(data[1:1+PF.BITMAP_SIZE])
            elif data[0] == PF.ID_SPECTRUM:
                self.draw_spec(data[1:1+PF.SPECTRUM_SIZE])
        except:
            pass

        """ 曲名を表示 """
        if self.is_display_enable:
            if self.is_scroll_enable:
                self.rest_scroll_sec += POLLING_SEC
                if self.rest_scroll_sec >= SCROLL_SEC:
                    self.rest_scroll_sec = 0
                    self.base_x -= 2
                    if self.base_x <= -len(self.bitmap) * 2:
                        self.base_x = WIN_WIDTH
            self.draw_bitmap(self.base_x, 0)

        """ 画面を更新 """
        self.win.refresh()
        curses.doupdate()

        return True

    def draw_spec(self, spec):
        y_pos = 0
        for y in range(32)[::-1]:
            x_pos = 0
            for x in spec:
                if x > y:
                    self.win.addstr(y_pos, x_pos, '______', curses.A_REVERSE)
                    self.win.addstr('| ')
                else:
                    self.win.addstr(y_pos, x_pos, '        ')
                x_pos += 8
            y_pos += 1

    def draw_bitmap(self, base_x, base_y):
        for x in range(len(self.bitmap)):
            draw_x = base_x + x*2
            if not (0 <= draw_x and draw_x < WIN_WIDTH - 1):
                continue
            for y in range(8):
                draw_y = base_y + y
                if not (0 <= draw_y and draw_y < WIN_HEIGHT - 1):
                    continue
                if self.bitmap[x] & (1<<y):
                    self.win.addstr(draw_y, draw_x, '  ', curses.A_REVERSE)
                else:
                    self.win.addstr(draw_y, draw_x, '  ')
