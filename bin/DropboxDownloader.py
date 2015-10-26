# -*- coding: utf-8 -*-
import urllib3
from dropbox import client, rest
import os

class DropboxDownloader:
    def __init__(self, token_path):
        self.api_client = None
        urllib3.disable_warnings()
        self.__oauth2(token_path)

    def __oauth2(self, token_path):
        with open(token_path) as f:
            serialized_token = f.read()
            if serialized_token.startswith('oauth2:'):
                access_token = serialized_token[len('oauth2:'):]
                self.api_client = client.DropboxClient(access_token)
            else:
                print('token error')       
        
    def do_ls(self):
        resp = self.api_client.metadata('')
        file_list = []
        if 'contents' in resp:
            for f in resp['contents']:
                name = os.path.basename(f['path'])
                file_list.append(name)
        return file_list

    def do_get(self, from_path, to_path):
        to_file = open(to_path, "wb")
        f, metadata = self.api_client.get_file_and_metadata(from_path)
        #print 'Metadata:', metadata
        to_file.write(f.read())
