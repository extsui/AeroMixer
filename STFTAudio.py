#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy as np
import scipy as sp
import pyaudio
import wave

"""
状態遷移予定

LOAD --> PLAY: start()
PLAY --> STOP: stop()
STOP --> PLAY: start()
PLAY --> INIT:  - (After require close())
INIT --> LOAD: load()

     + ----------------+
     v                 |
==> INIT --> LOAD --> PLAY
                       ^
                       |
                       v
                      STOP
"""
class STFTAudio:
    STFT_SIZE = 4096

    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.stream = None
        self.wavefile = None
        self.wavedata = None
        self.hamming_win = sp.hamming(self.STFT_SIZE)
        self.frame_pos = 0

    def __callback(self, in_data, frame_count, time_info, status):
        self.frame_pos += frame_count
        data = self.wavefile.readframes(frame_count)
        return (data, pyaudio.paContinue)

    def open(self, wavefile):
        self.wavefile = wave.open(wavefile, 'rb')
        frames = self.wavefile.readframes(self.wavefile.getnframes())
        # -1~+1の範囲に正規化
        self.wavedata = sp.fromstring(frames, dtype='int16') / 32768.0
        self.wavefile.rewind()
        self.stream = self.pa.open(format=self.pa.get_format_from_width(self.wavefile.getsampwidth()),
                                   channels=self.wavefile.getnchannels(),
                                   rate=self.wavefile.getframerate(),
                                   output=True,
                                   stream_callback=self.__callback)
    
    """
    |-------+-----------+------------|
    | state | is_active | is_stopped |
    |-------+-----------+------------|
    | INIT  | F         | F          |
    | LOAD  | F         | F          |
    | PLAY  | T         | F          |
    | STOP  | F         | T          |
    |-------+-----------+------------|
    """
    def is_playing(self):
        return self.stream.is_active() and not self.stream.is_stopped()

    def is_stopping(self):
        return not self.stream.is_active() and self.stream.is_stopped()

    def start(self):
        self.stream.start_stream()

    def stop(self):
        self.stream.stop_stream()

    def stft(self):
        fscale_hotspot = [2, 3, 4, 5, 6, 7, 8, 9, 12, 14, 18, 22, 27, 34, 43, 53, 66, 83, 103, 129, 161, 201, 251, 313, 391, 488, 610, 762, 952, 1190, 1487, 1858]
        x = self.wavedata[self.frame_pos:self.frame_pos+self.STFT_SIZE]
        # 一番最後はSTFTできないのでゼロ埋めダミーデータで代用
        if len(x) != self.STFT_SIZE:
            return map(int, np.zeros(len(fscale_hotspot)))
        X = sp.fft(x * self.hamming_win)
        # 振幅スペクトルの計算(パワースペクトルは重いのでやらない)
        spectrum = np.abs(X[fscale_hotspot])
        # 値が0-32あたりに収まるように調整
        spectrum = np.sqrt(spectrum) * 2
        spectrum = map(int, spectrum)
        return spectrum

    def close(self):
        self.stop()
        self.stream.close()
        self.wavefile.close()
        self.pa.terminate()

if __name__ == '__main__':
    import sys
    argv = sys.argv
    argc = len(argv)
    if argc != 2:
        print(argv[0] + ' <mono-wavefile>')
        exit(-1)
    wavefile = argv[1]

    stft = STFTAudio()
    stft.open(wavefile)
    stft.start()

    while stft.is_playing() or stft.is_stopping():
        import time
        s = raw_input('(s|p|f)> ')
        if s == 's':
            stft.start()
        elif s == 'p':
            stft.stop()
        elif s == 'f':
            print stft.stft()

    stft.close()
    print('play end.')
