#!/usr/bin/python
# -*- coding: utf-8 -*-
import threading
import curses
import FontManager
import numpy as np

WIN_WIDHT = 256
WIN_HEIGHT = 32

class ScreenThread(threading.Thread):
    def __init__(self, dev_so, kill_event):
        """
        ・ホストと通信するためのソケット
        ・タイムアウト有りのブロッキング動作
        """
        self.dev_so = dev_so
        self.dev_so.setblocking(1)
        self.dev_so.settimeout(0.050)
        """ ホストからのスレッド終了命令用 """
        self.kill_event = kill_event
        super(ScreenThread, self).__init__()

    def run(self):
        curses.wrapper(self.curses_main)

    def curses_main(self, stdscr):
        """ エコーバックOFF，バッファリングOFF """
        curses.noecho()
        curses.cbreak()

        """ 
        ・新規ウィンドウを作成
        ・表示タイミングをdoupdate()時に設定
        ・getch()を非ブロッキング動作に設定
        """
        self.win = curses.newwin(WIN_HEIGHT, WIN_WIDHT)
        self.win.noutrefresh()
        self.win.timeout(0)

        while not self.kill_event.is_set():
            self.main_loop()

    def main_loop(self):
        """ 入力の有無を確認し，あればホストに送信 """
        c = self.win.getch()
        if c is not curses.ERR:
            if 0 <= c and c <= 255:
                self.dev_so.send(chr(c))

        """ 受信に成功したら対応する処理を実行し，タイムアウト時はnop """
        try:
            spec = self.dev_so.recv(32)
            spec = np.fromstring(spec, dtype=np.uint8)
            self.draw_spec(spec)
        except:
            pass
        
        """ 画面を更新 """
        self.win.refresh()
        curses.doupdate()

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
