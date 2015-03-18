#!/usr/bin/python

from twisted.web import server, resource
from twisted.internet import reactor, defer
from configobj import ConfigObj
import logging
import time
import sys
import argparse
import simplejson
import os

LOG = logging.getLogger("ssfiless")

class SSFileServer(resource.Resource):

    isLeaf = True

    def __init__(self):
        self.db = ConfigObj('ssfilesss.conf')
        self.files_section = self.db['files']

        self.storage_location = self.db['general']['storage_location']
        if not os.path.exists(self.storage_location):
            os.makedirs(self.storage_location)


    def getChild(self, name, request):
        LOG.debug('getting child: %s' % name)
        if not name:
            return self
        return resource.Resource.getChild(self, name, request)

    def _upload(self, request):
        data = simplejson.loads(request.content.read())

        LOG.debug('%s:handling request: %s', self.__class__.__name__, data)

        upload_result = {'link': None}

        #....................

        result = simplejson.dumps({'result':upload_result})
        return result

    def render_POST(self, request):
        LOG.debug('render_GET: uri=%s', request.uri)
        d = defer.maybeDeferred(self._upload, request)
        d.addCallback(self._upload_ready, request)
        d.addErrback(self._upload_error, request)
        return server.NOT_DONE_YET

    def _upload_ready(self, result, request):
        LOG.debug('\tresult --> %s', result)
        request.write(result)
        request.finish()

    def _upload_error(self, failure, request):
        LOG.debug('\t--> %s', failure)
        failure = {'error':str(failure.value)}
        request.write(simplejson.dumps(failure))
        request.finish()



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
    #root.putChild('greedy', WBSRouteMsgGreedy())
    #root.putChild('greedy2', WBSRouteMsgGreedy2())
    site = server.Site(root)
    reactor.listenTCP(8080,site)
    reactor.run()



