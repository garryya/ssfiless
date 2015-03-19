#!/usr/bin/python

from twisted.web import server, resource
from twisted.internet import reactor, defer
from twisted.internet.defer import  inlineCallbacks, returnValue
from twisted.internet.task import LoopingCall
from configobj import ConfigObj
import logging
import sys
import argparse
import simplejson
import os
import re
import uuid
import time
from datetime import datetime
import commands
from tempfile import mkstemp, mktemp

LOG = logging.getLogger("ssfiless")

class FileNotFoundException(Exception):
    def __init__(self,fname=''):
        self._fname = fname
    def __str__(self):
        return 'File not found: %s' % self._fname
class FileCryptoFailed(Exception):
    def __init__(self,fname=''):
        self._fname = fname
    def __str__(self):
        return 'File encryption failed: %s' % self._fname


def runcmd( cmd, ignore_status=False):
    status, output = commands.getstatusoutput( cmd )
    if status != 0 and not ignore_status:
        LOG.error("error running <%s> : %d <%s>", cmd, status, output)
        return status, None
    LOG.info("running <%s> --> s=%d", cmd, status)
    return status, output

class SecTempFile:
    def __init__(self):
        self.fname = mktemp()
    def _delete(self):
        runcmd("rm -f %s" % self.fname)
    def __enter__(self):
        return self
    def __exit__(self, type, value, traceback):
        self._delete()

def use_filename_only(f):
    def _f(*args,**kwargs):
        args = (args[0], os.path.basename(args[1])) + args[2:]
        return f(*args,**kwargs)
    return _f

class SSFileServerDB:
    def __init__(self, dbname):
        LOG.debug('Loading DB & configuration from %s...', dbname)
        self._db = ConfigObj(dbname)
        self._files_section = self._db['files']
        for e in self._db['general']:
            self.__dict__[e] = self._db['general'][e]

    def read_all_files(self):
        return ((f,self._files_section[f]) for f in self._files_section)

    @use_filename_only
    def read_file(self, fname):
        return self._files_section[fname]

    @use_filename_only
    def file_exists(self, fname):
        fname = os.path.basename(fname)
        return fname in self._files_section

    @use_filename_only
    def add_file(self, fname, fdata):
        fname = os.path.basename(fname)
        self._files_section[os.path.basename(fname)] = fdata
        self._db.write()

    @use_filename_only
    def delete_file(self, fname):
        del self._files_section[fname]
        self._db.write()


class SSFileServer(resource.Resource):

    isLeaf = True

    def __init__(self, config=None):
        self._db = SSFileServerDB(config if config else 'ssfilesss.conf')
        self._storage_location = os.path.abspath(self._db.storage_location)
        if not os.path.exists(self._storage_location):
            os.makedirs(self._storage_location)
        self._cleanupLoop = LoopingCall(self._cleanup)
        self._cleanupLoop.start(int(self._db.cleanup_loop_interval)*60)

    def _get_public_ip_amazon(self):
        s, o = runcmd('curl -s --connect-timeout 2 http://169.254.169.254/latest/meta-data/public-hostname')
        if s or not o:
            return None
        return o

    def _get_public_ip(self):
        ip = self._get_public_ip_amazon()
        if not ip:
            ip = re.search( r'inet ([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+).*eth0', commands.getoutput('ip a') ).groups()[0]
        return ip

    def _uri(self, fname):
        return 'http://%s:8080/%s' % (self._get_public_ip(), fname)

    def _get_local_file_path(self, fname):
        return os.path.join(self._storage_location, fname)

    def _file_exists(self, path, check_db_only=False):
        return self._db.file_exists(path) and (check_db_only or os.path.exists(path))

    def _generate_file_name(self, prefix=None):
        fname = ''
        if prefix:
            fname += prefix + '_'
        return fname + str(uuid.uuid4())

    def _ready(self, result, request):
        #LOG.debug('\tresult --> %s', result)
        request.write(result)
        request.finish()

    def _error(self, failure, request):
        LOG.debug('\t--> %s', failure)
        failure = {'error':str(failure.value)}
        request.write(simplejson.dumps(failure))
        request.finish()

    def _encrypt_file(self, path):
        ''' Encrypts a file with created key, replaces the original and returns the key
        '''
        key = str(uuid.uuid4())
        s, o = runcmd('openssl aes-256-cbc -a -salt -in %s -pass pass:%s -out %s.enc' % (path, key, path))
        if s:
            return False, None
        s, o = runcmd('mv %s.enc %s' % (path, path))
        if s:
            return False, None
        return True, key

    def _decrypt_file(self, path, key, tempfile):
        ''' Decrypts a file into temp file, file will be removed immediately after sending
        '''
        s, o = runcmd('openssl aes-256-cbc -a -d -in %s -pass pass:%s -out %s' % (path, key, tempfile))
        if s:
            return False
        return True

    ##################

    @inlineCallbacks
    def _upload(self, request):
        LOG.debug('Uploading...')
        local_file_path = os.path.join(self._storage_location, self._generate_file_name())
        with open(local_file_path,'w') as f:
            f.write(request.content.read())

        encrypted, key = yield self._encrypt_file(local_file_path)
        if not encrypted:
            request.setResponseCode(500) # internal
            raise FileCryptoFailed()

        yield self._db.add_file(local_file_path, {'created':time.time(), 'completed':True, 'key':key})
        result = self._uri(os.path.basename(local_file_path))
        LOG.debug('\tdone (%s)', result)
        returnValue(result)

    def render_POST(self, request):
        LOG.debug('render_POST: uri=%s', request.uri)
        d = defer.maybeDeferred(self._upload, request)
        d.addCallback(self._ready, request)
        d.addErrback(self._error, request)
        return server.NOT_DONE_YET

    #################

    def _delete_file(self, file_path):
        self._db.delete_file(file_path)
        try:
            os.remove(file_path)
        except:
            pass

    @inlineCallbacks
    def _delete(self, request):
        fname = request.uri[1:]
        local_file_path = self._get_local_file_path(fname)
        LOG.debug('Deleting file %s...', local_file_path)
        exists = yield self._file_exists(local_file_path, check_db_only=True)
        if not exists:
            request.setResponseCode(404)
            raise FileNotFoundException(fname)
        self._delete_file(local_file_path)
        returnValue('')

    def render_DELETE(self, request):
        LOG.debug('render_DELETE: uri=%s', request.uri)
        d = defer.maybeDeferred(self._delete, request)
        d.addCallback(self._ready, request)
        d.addErrback(self._error, request)
        return server.NOT_DONE_YET


    #################

    @inlineCallbacks
    def _get_content(self, request):
        fname = request.uri[1:]
        local_file_path = self._get_local_file_path(fname)
        LOG.debug('File content request %s', local_file_path)
        if not self._file_exists(local_file_path):
            request.setResponseCode(404)
            raise FileNotFoundException(fname)
        fdata = yield self._db.read_file(local_file_path)
        result = None
        with SecTempFile() as sf:
            decrypted = yield self._decrypt_file(local_file_path, fdata['key'], sf.fname)
            if not decrypted:
                request.setResponseCode(500) # internal
                raise FileCryptoFailed()
            result = open(sf.fname,'rb').read()
        returnValue(result)

    def render_GET(self, request):
        LOG.debug('render_GET: uri=%s', request.uri)
        d = defer.maybeDeferred(self._get_content, request)
        d.addCallback(self._ready, request)
        d.addErrback(self._error, request)
        return server.NOT_DONE_YET

    def _cleanup(self):
        max_file_age_seconds = int(self._db.max_file_age_seconds)
        max_file_age_days = int(self._db.max_file_age_days)
        LOG.debug('Cleaning up... (s=%d, d=%s)', max_file_age_seconds, max_file_age_days)
        for f, fdata in self._db.read_all_files():
            tdelta = datetime.fromtimestamp(time.time()) - datetime.fromtimestamp(float(fdata['created']))
            if max_file_age_seconds != -1 and tdelta.seconds >= max_file_age_seconds or tdelta.days >= max_file_age_days:
                self._delete_file(self._get_local_file_path(f))



ap = argparse.ArgumentParser()
ap.add_argument('--debug', action='store_const', dest='isDebug', const=True, default=False)
ap.add_argument('--config')
rap = ap.parse_args()
if rap.isDebug:
    print 'Debug mode is ON'

if __name__ == '__main__':
    filename = __file__[:__file__.rfind('.')+1]
    FMT = "%(asctime)s - %(name)-6s - %(levelname)-6s - [%(filename)s:%(lineno)d] - %(message)s"
    logging.basicConfig(filename='/var/log/'+os.path.basename(filename)+'log',
                        level=logging.DEBUG if rap.isDebug else logging.INFO,
                        format=(FMT))
    if rap.isDebug:
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(logging.Formatter(FMT))
        LOG.addHandler(ch)

    LOG.info('Starting service...')
    root = SSFileServer(rap.config)
    site = server.Site(root)
    reactor.listenTCP(8080,site)
    reactor.run()



