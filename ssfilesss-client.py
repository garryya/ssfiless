#!/usr/bin/python

import sys
import os
import argparse
import httplib2
from datetime import datetime
import simplejson

file_actions = ['upload', 'get', 'delete']

ap = argparse.ArgumentParser()
ap.add_argument('--server', required=True)
ap.add_argument('--action', choices=file_actions, required=True)
ap.add_argument('--debug', action='store_const', dest='isDebug', const=True, default=False)
ap.add_argument('--path')
rap = ap.parse_args()
#print rap

if rap.action in file_actions and not rap.path:
    print 'Please specify path or link for <', rap.action, '>'

if rap.isDebug:
    print 'Debug mode is ON'

def success(resp, content):
    return 'error' not in content

def URI(action):
    return 'http://%s:8080/%s' % (rap.server, action)

def upload_file():
    print 'Uploading file', rap.path, '...'
    file_name = os.path.abspath(rap.path)
    h = httplib2.Http()
    resp, content = h.request(URI(rap.action),
                              'POST',
                              open(file_name,'rb').read(),
                              headers={'Content-Type': 'application/octet-stream'})
    #TODO really - eval ??
    print content
    print 'Upload%s' % (' failed' if not success(resp, content) else 'ed')


def get_file_content():
    #print 'Getting remote file content', rap.path, '...'
    h = httplib2.Http()
    resp, content = h.request(URI(rap.path),
                              'GET',
                              simplejson.dumps({}),
                              headers={'Content-Type': 'application/octet-stream'})

    if not success(resp, content):
        print 'File content request failed'
    print content

def delete_file():
    print 'Getting remote file content', rap.path, '...'
    h = httplib2.Http()
    resp, content = h.request(URI(rap.path),
                              'DELETE',
                              simplejson.dumps({}),
                              headers={'Content-Type': 'application/json'})

    print 'File delet%s' % ('ion failed' if not success(resp, content) else 'ed')


def upload_folder():
    print 'Uploading folder', rap.path, '...'
    raise NotImplementedError

if __name__ == '__main__':

    try:
        if rap.action == 'upload':
            if not os.path.exists(rap.path):
                print 'The path does not exist:', rap.path
                sys.exit(1)

            if not os.path.isdir(rap.path):
                upload_file()
            else:
                upload_folder()

        elif rap.action == 'get':
            get_file_content()
        elif rap.action == 'delete':
            delete_file()
        else:
            print 'Unknown action <', rap.action, '>'

    except Exception as e:
        print 'Exception: ', repr(e)
        sys.exit(1)



