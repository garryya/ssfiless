#!/usr/bin/python

from twisted.web import server, resource
from twisted.internet import reactor, defer
from configobj import ConfigObj
import logging
import commands
import sys
import argparse
import simplejson
import os
import re


LOG = logging.getLogger("ssfiless")


class FileNotFoundException(Exception):
    def __init__(self,fname=''):
        self._fname = fname
    def __str__(self):
        return 'File not found: %s' % self._fname


class SSFileServer(resource.Resource):

    isLeaf = True

    def __init__(self):
        self.db = ConfigObj('ssfilesss.conf')
        self._files_section = self.db['files']
        self._storage_location = os.path.abspath(self.db['general']['storage_location'])
        if not os.path.exists(self._storage_location):
            os.makedirs(self._storage_location)

    #TODO - questionable...
    def _uri(self, folder, fname):
        ip = re.search( r'inet ([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+).*eth0', commands.getoutput('ip a') ).groups()[0]
        return 'http://%s:8080/%s' % (ip, os.path.join(folder, fname))

    def _get_local_path(self, fname):
        return os.path.join(self._storage_location, fname)

    def _file_exists(self, path):
        return path in self._files_section and os.path.exists(path)

    def _ready(self, result, request):
        LOG.debug('\tresult --> %s', result)
        request.write(result)
        request.finish()

    def _error(self, failure, request):
        LOG.debug('\t--> %s', failure)
        failure = {'error':str(failure.value)}
        request.write(simplejson.dumps(failure))
        request.finish()

    ##################

    def _upload(self, request):
        data = simplejson.loads(request.content.read())

        LOG.debug('Upload request %s', data)

        folder = data['folder'] if 'folder' in data and data['folder'] else ''
        upload_result = self._uri(folder, data['file'])

        #....................

        result = upload_result #simplejson.dumps(upload_result)
        return result

    def render_POST(self, request):
        LOG.debug('render_POST: uri=%s', request.uri)
        d = defer.maybeDeferred(self._upload, request)
        d.addCallback(self._ready, request)
        d.addErrback(self._error, request)
        return server.NOT_DONE_YET

    #################

    def _get_content(self, request):
        fname = os.path.basename(request.uri)
        local_path = self._get_local_path(fname)
        LOG.debug('File content request %s', local_path)

        ###TODO check DB first !!!!!
        if not self._file_exists(local_path):
            request.setResponseCode(404)
            raise FileNotFoundException(fname)
        result = 'XXX'
        return result

    def render_GET(self, request):
        LOG.debug('render_GET: uri=%s', request.uri)
        d = defer.maybeDeferred(self._get_content, request)
        d.addCallback(self._ready, request)
        d.addErrback(self._error, request)
        return server.NOT_DONE_YET





ap = argparse.ArgumentParser()
ap.add_argument('--debug', action='store_const', dest='isDebug', const=True, default=False)
rap = ap.parse_args()
if rap.isDebug:
    print 'Debug mode is ON'

if __name__ == '__main__':
    filename = __file__[:__file__.rfind('.')+1]
    FMT = "%(asctime)s - %(name)-6s - %(levelname)-6s - [%(filename)s:%(lineno)d] - %(message)s"
    logging.basicConfig(filename=filename+'log',
                        level=logging.DEBUG if rap.isDebug else logging.INFO,
                        format=(FMT))
    if rap.isDebug:
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(logging.Formatter(FMT))
        LOG.addHandler(ch)

    LOG.info('Starting service...')
    root = SSFileServer()
    site = server.Site(root)
    reactor.listenTCP(8080,site)
    reactor.run()



