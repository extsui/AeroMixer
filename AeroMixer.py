#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import locale
import sys
import subprocess

from pprint import pprint

from dropbox import client, rest
import urllib3

api_client = None

def dropbox_authorization(token_file):
    global api_client
    with open(token_file) as f:
        serialized_token = f.read()
        if serialized_token.startswith('oauth2:'):
            access_token = serialized_token[len('oauth2:'):]
            api_client = client.DropboxClient(access_token)
        else:
            print('token error')
            exit

def download_mp3_file_list():
    resp = api_client.metadata('')
    mp3_file_list = []
    if 'contents' in resp:
        for f in resp['contents']:
            name = os.path.basename(f['path'])
            if name.endswith('.mp3'):
                mp3_file_list.append(f)
                #encoding = locale.getdefaultlocale()[1] or 'ascii'
                #sys.stdout.write(('%s\n' % name).encode(encoding))

    return mp3_file_list

def download_file(from_path, to_path):
    to_file = open(os.path.expanduser(to_path), "wb")
    f, metadata = api_client.get_file_and_metadata(from_path)
    #print 'Metadata:', metadata
    to_file.write(f.read())

if __name__ == '__main__':
    TOKEN_FILE = 'token_store.txt'

    urllib3.disable_warnings()
    dropbox_authorization(TOKEN_FILE)
    mp3_file_list = download_mp3_file_list()

    for mp3_file in mp3_file_list:
        from_path = mp3_file['path']
        to_path = '/tmp' + from_path

        #pprint(mp3_file)
        print(from_path + ': ' + mp3_file['size'])
        print('Downloading mp3 ...')
        download_file(from_path, to_path)

        mp3_path = to_path
        wav_path = mp3_path.replace('.mp3', '.wav')

        print('mp3:' + mp3_path)
        print('wav:' + wav_path)

        print('Converting mp3 to wav ...')
        # 標準エラー出力が鬱陶しいので見えなくする
        subprocess.call(["ffmpeg", "-i", mp3_path,
                         "-ac", "1", "-ar", "44100", wav_path],
                        stderr=-1)

        print('Playing wav ...')
        subprocess.call(["aplay", "-q", wav_path])

        print('Cleaning mp3 and wav ...')
        os.unlink(mp3_path)
        os.unlink(wav_path)
