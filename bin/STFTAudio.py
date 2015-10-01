#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy as np
import scipy as sp
import pyaudio
import wave

class STFTAudio:
    """ スペクトル表示のパラメータ """
    STFT_SIZE = 4096
    FREQ_PROBE_NUM = 32
    LOWER_HERTZ = 20.
    UPPER_HERTZ = 20000.

    """ FFTの周期(秒単位) """
    STFT_INTERVAL = 0.050

    """
    周波数範囲[lower_hertz:upper_hertz]を対数スケールで
    freq_probe_numだけ区切った要素配列を作成する．
    """
    def __fftprobe(self, fft_size, freq_probe_num, lower_hertz, upper_hertz):
        freq_list = np.fft.fftfreq(fft_size, 1.0/44100)
        freq_probe_list = [lower_hertz *
                             ((upper_hertz/lower_hertz) ** (x/(freq_probe_num-1.0)))
                             for x in range(freq_probe_num)]
        freq_probe_index_list = []
        probe_index = 0

        for i in range(fft_size):
            # 近い周波数値の取得
            # 連続する2つの周波数値を取得して小さい誤差の方を取り出すのが
            # 本来ならば望ましい．しかし，そうした場合，取得するポイント数が
            # 多すぎるとうまく配列を構成できない(FFT_SIZE=4096, num=32)．
            # このため，誤差は大きくなるが，1つの周波数値だけ確認している．
            if freq_list[i] > freq_probe_list[probe_index]:
                freq_probe_index_list.append(i)
                probe_index += 1
                if probe_index >= freq_probe_num:
                    break

        if probe_index is not freq_probe_num:
            raise ValueError('FREQ_PROBE_NUM is too large compared to STFT_SIZE')

        # --- debug ---
        #print('      index    Freq')
        #for index in freq_probe_index_list:
        #    print('%3d: [%5d] %8f' % (freq_probe_index_list.index(index),
        #                              index, freq_list[index]))

        return freq_probe_index_list

    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.stream = None
        self.wavefile = None
        self.wavedata = None
        self.hamming_win = sp.hamming(self.STFT_SIZE)
        self.frame_pos = 0
        self.freq_probe_index_list = self.__fftprobe(self.STFT_SIZE,
                                                     self.FREQ_PROBE_NUM,
                                                     self.LOWER_HERTZ,
                                                     self.UPPER_HERTZ)

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
        x = self.wavedata[self.frame_pos:self.frame_pos+self.STFT_SIZE]
        # 一番最後はSTFTできないのでゼロ埋めダミーデータで代用
        if len(x) != self.STFT_SIZE:
            return map(int, np.zeros(len(self.freq_probe_index_list)))
        X = sp.fft(x * self.hamming_win)
        # 振幅スペクトルの計算(パワースペクトルは重いのでやらない)
        spectrum = np.abs(X[self.freq_probe_index_list])
        # 値が0-32あたりに収まるように調整
        spectrum = np.sqrt(spectrum) * 2
        spectrum = map(int, spectrum)
        return spectrum

    def close(self):
        self.frame_pos = 0
        self.stop()
        self.stream.close()
        self.wavefile.close()

    def __del__(self):
        """
        close()で行っていたが，2度目のopen()に失敗するため，
        デストラクタでterminate()を呼び出す．
        """
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
