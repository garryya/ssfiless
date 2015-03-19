#!/usr/bin/python

import sys
import os
import argparse
import httplib2
import simplejson
from twisted.internet import reactor
from twisted.internet.defer import  inlineCallbacks, returnValue, DeferredList
import logging

LOG = logging.getLogger("ssfiless-client")

file_actions = ['upload', 'get', 'delete']

ap = argparse.ArgumentParser()
ap.add_argument('--server', required=True)
ap.add_argument('--action', choices=file_actions, required=True)
ap.add_argument('--path')
rap = ap.parse_args()

if rap.action in file_actions and not rap.path:
    print 'Please specify path or link for <', rap.action, '>'
    sys.exit(1)

def success(resp, content):
    return resp['status'] == '200' and '\'error\':' not in content

def URI(action):
    return 'http://%s:8080/%s' % (rap.server, action)

@inlineCallbacks
def upload_file(path=None):
    if not path:
        path = rap.path
    LOG.debug('Uploading file %s...', path)
    file_name = os.path.abspath(path)
    h = httplib2.Http()
    resp, content = yield h.request(URI(rap.action),
                              'POST',
                              open(file_name,'rb').read(),
                              headers={'Content-Type': 'application/octet-stream'})
    #LOG.debug('Upload%s' % (' failed' if not success(resp, content) else 'ed'))
    if not success(resp, content):
        LOG.error('Upload failed: %s / %s', resp, content)
        returnValue('Failed')
    returnValue(content)


def get_file_content():
    LOG.debug('Getting remote file content %s....', rap.path)
    h = httplib2.Http()
    resp, content = h.request(URI(rap.path),
                              'GET',
                              simplejson.dumps({}),
                              headers={'Content-Type': 'application/octet-stream'})

    if not success(resp, content):
        LOG.error('Get file content failed: %s / %s', resp, content)
        return None
    return content

def delete_file():
    LOG.debug('Deleting remote file %s...', rap.path)
    h = httplib2.Http()
    resp, content = h.request(URI(rap.path),
                              'DELETE',
                              simplejson.dumps({}),
                              headers={'Content-Type': 'application/json'})
    if not success(resp, content):
        LOG.error('File delete failed: %s / %s', resp, content)
        return content
    return None


##########################################

def listdirs(path):
    return (os.path.join(path,f) for f in os.listdir(path) if os.path.isdir(os.path.join(path,f)))
def listfiles(path):
    return (os.path.abspath(os.path.join(path,f)) for f in os.listdir(path) if not os.path.isdir(os.path.join(path,f)))

@inlineCallbacks
def _upload_folder(path):
    yield
    if not os.path.isdir(path):
        return
    for f in listdirs(path):
        _upload_folder(f)
    uploads = [upload_file(f) for f in listfiles(path)]
    dl = DeferredList(uploads, consumeErrors=True)
    ret = yield dl
    ret = ''.join([t[1]+'\n' for t in ret if t[0]]).strip()
    returnValue(ret)

def upload_folder():
    LOG.debug('Uploading folder %s...', rap.path)
    return _upload_folder(rap.path)

@inlineCallbacks
def main():
    try:
        ret = None
        if rap.action == 'upload':
            if not os.path.exists(rap.path):
                print 'The path does not exist:', rap.path
                sys.exit(1)

            if not os.path.isdir(rap.path):
                ret = yield upload_file()
            else:
                ret = yield upload_folder()
        elif rap.action == 'get':
            ret = get_file_content()
        elif rap.action == 'delete':
            ret = delete_file()
        else:
            print 'Unknown action <', rap.action, '>'
            sys.exit(1)
        if ret:
            print ret

    except Exception as e:
        print 'Exception: ', repr(e)
        sys.exit(1)
    finally:
        reactor.stop()

if __name__ == '__main__':
    filename = __file__[:__file__.rfind('.')+1]
    FMT = "%(asctime)s - %(name)-6s - %(levelname)-6s - [%(filename)s:%(lineno)d] - %(message)s"
    logging.basicConfig(filename='/var/log/'+os.path.basename(filename)+'log',
                        level=logging.DEBUG,
                        format=(FMT))

    reactor.callWhenRunning(main)
    reactor.run()

