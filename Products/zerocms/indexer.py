from logging import getLogger
import json, requests
from Acquisition import aq_get
from DateTime import DateTime
from datetime import date, datetime
from zope.component import getUtility, queryUtility, queryMultiAdapter
from zope.interface import implements
from ZODB.POSException import ConflictError
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
from Products.Archetypes.CatalogMultiplex import CatalogMultiplex
from plone.app.content.interfaces import IIndexableObjectWrapper
from plone.indexer.interfaces import IIndexableObject

from collective.solr.solr import SolrException
from collective.solr.utils import prepareData
from socket import error

from Products.zerocms.interfaces import (
IZeroCMSIndexQueueProcessor, IRequestFactory,
IZeroCMSSchema, IZeroCMSSettings)
from Products.zerocms.mapper import DataMapper

logger = getLogger('Products.zerocms.indexer')

def indexable(obj):
    """ indicate whether a given object should be indexed; for now only
        objects inheriting one of the catalog mixin classes are considered """
    return isinstance(obj, CatalogMultiplex) or \
        isinstance(obj, CMFCatalogAware)


class RequestFactory(object):
    implements(IRequestFactory)

    def __init__(self):
        print "\nCreating new RequestFactory\n"
        config = queryUtility(IZeroCMSSettings)
        if config is not None:
            self.post_url = config.post_url

    def save(self, values):
        print "Save called with url: " + self.post_url
        requests.post(self.post_url, json.dumps(values))


class ZeroCMSIndexProcessor(object):
    """ a queue processor for zerocms """
    implements(IZeroCMSIndexQueueProcessor)

    def __init__(self, requestFactory=None):
        logger.info("Starting Zeo procesor")
        self.config = queryUtility(IZeroCMSSettings)
        self.requestFactory = requestFactory
        if requestFactory is None:
            self.requestFactory = getUtility(IRequestFactory)

    def begin(self):
        """ called before processing of the queue is started """
        pass

    def commit(self):
        """ called after processing of the queue has ended """
        pass

    def abort(self):
        """ called if processing of the queue needs to be aborted """
        pass

    def index(self, obj, attributes=None):
        print "Index called: " + repr(obj.__dict__)

        mapper = DataMapper(self.config.instance_id, self.config.instance_url)
        

        obj = self.wrapObject(obj)
        data= mapper.convert(obj)
        print "Got data: \n%s" % repr(data)
        self.requestFactory.save(data)

        return
    def reindex(self, obj, attributes=None):
        self.index(obj, attributes)

    def unindex(self, obj):
        conn = self.getConnection()
        if conn is not None:
            schema = self.requestFactory.getSchema()
            if schema is None:
                msg = 'unable to fetch schema, skipping unindexing of %r'
                logger.warning(msg, obj)
                return
            uniqueKey = schema.get('uniqueKey', None)
            if uniqueKey is None:
                msg = 'schema is missing unique key, skipping unindexing of %r'
                logger.warning(msg, obj)
                return
            data, missing = self.getData(obj, attributes=[uniqueKey])
            prepareData(data)
            if not uniqueKey in data:
                msg = 'Can not unindex: no unique key for object %r'
                logger.info(msg, obj)
                return
            data_key = data[uniqueKey]
            if data_key is None:
                msg = 'Can not unindex: `None` unique key for object %r'
                logger.info(msg, obj)
                return
            try:
                logger.debug('unindexing %r (%r)', obj, data)
                conn.delete(id=data_key)
            except (SolrException, error):
                logger.exception('exception during unindexing %r', obj)


    def getConnection(self):
        if self.requestFactory is None:
            self.requestFactory = queryUtility(ISolrConnectionManager)
        if self.requestFactory is not None:
            self.requestFactory.setIndexTimeout()
            return self.requestFactory.getConnection()

    def wrapObject(self, obj):
        """ wrap object with an "IndexableObjectWrapper` (for Plone < 3.3) or
            adapt it to `IIndexableObject` (for Plone >= 3.3), see
            `CMFPlone...CatalogTool.catalog_object` for some background """
        wrapper = obj
        # first try the new way, i.e. using `plone.indexer`...
        catalog = getToolByName(obj, 'portal_catalog', None)
        adapter = queryMultiAdapter((obj, catalog), IIndexableObject)
        if adapter is not None:
            wrapper = adapter
        else:       # otherwise try the old way...
            portal = getToolByName(obj, 'portal_url', None)
            if portal is None:
                return obj
            portal = portal.getPortalObject()
            adapter = queryMultiAdapter((obj, portal), IIndexableObjectWrapper)
            if adapter is not None:
                wrapper = adapter
            wft = getToolByName(obj, 'portal_workflow', None)
            if wft is not None:
                wrapper.update(wft.getCatalogVariablesFor(obj))
        return wrapper

