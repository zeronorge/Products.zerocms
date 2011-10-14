from logging import getLogger
from time import time, clock, strftime

from zope.interface import implements
from zope.component import queryUtility
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from collective.indexing.indexer import getOwnIndexMethod
from collective.solr.utils import findObjects
from Products.zerocms.interfaces import IZeroCMSMaintenanceView, IZeroCMSIndexQueueProcessor
from Products.zerocms.indexer import IRequestFactory
from collective.solr.indexer import indexable

logger = getLogger('collective.solr.maintenance')
MAX_ROWS = 1000000000


def timer(func=time):
    """ set up a generator returning the elapsed time since the last call """
    def gen(last=func()):
        while True:
            elapsed = func() - last
            last = func()
            yield '%.3fs' % elapsed
    return gen()


def checkpointIterator(function, interval=100):
    """ the iterator will call the given function for every nth invocation """
    counter = 0
    while True:
        counter += 1
        if counter % interval == 0:
            function()
        yield None



class ZeroCMSMaintenanceView(BrowserView):
    """ helper view for indexing all portal content in ZeroCMS """
    implements(IZeroCMSMaintenanceView)

    def mklog(self):
        """ helper to prepend a time stamp to the output """
        write = self.request.RESPONSE.write
        def log(msg, timestamp=True):
            if timestamp:
                msg = strftime('%Y/%m/%d-%H:%M:%S ') + msg
            write(msg)
        return log

    def reindex(self, batch=1000, skip=0):
        """ find all contentish objects (meaning all objects derived from one
            of the catalog mixin classes) and (re)indexes them """
        requestFactory = queryUtility(IRequestFactory)
        indexProcessor = queryUtility(IZeroCMSIndexQueueProcessor, name="zerocms")
        zodb_conn = self.context._p_jar
        log = self.mklog()
        log('reindexing documents to ZeroCMS...\n')
        if skip:
            log('skipping indexing of %d object(s)...\n' % skip)
        real = timer()          # real time
        lap = timer()           # real lap time (for intermediate commits)
        cpu = timer(clock)      # cpu time
        processed = 0
        updates = {}            # list to hold data to be updated
        count = 0
        for path, obj in findObjects(self.context):
            if indexable(obj):
                if getOwnIndexMethod(obj, 'indexObject') is not None:
                    log('skipping indexing of %r via private method.\n' % obj)
                    continue
                count += 1
                if count <= skip:
                    continue
                indexProcessor.index(obj)
                processed += 1
        zodb_conn.cacheGC();
        log('All documents exported to ZeroCMS.\n')
        msg = 'processed %d items in %s (%s cpu time).'
        msg = msg % (processed, real.next(), cpu.next())
        log(msg)
        logger.info(msg)

