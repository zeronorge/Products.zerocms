from logging import getLogger
import json, requests
from Acquisition import aq_get
from DateTime import DateTime
from datetime import date, datetime
from zope.component import getUtility, queryUtility, queryMultiAdapter
from plone.registry.interfaces import IRegistry

from zope.interface import implements, implementedBy, providedBy, classImplementsOnly, directlyProvidedBy
from ZODB.POSException import ConflictError
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
from Products.Archetypes.CatalogMultiplex import CatalogMultiplex

from plone.app.content.interfaces import IIndexableObjectWrapper
from plone.indexer.interfaces import IIndexableObject

from collective.solr.solr import SolrException
from collective.solr.utils import prepareData
from socket import error

from Products.zerocms.interfaces import *
from Products.zerocms.mapper import DataMapper



logger = getLogger('Products.zerocms.indexer')

def indexable(obj):
    """ indicate whether a given object should be indexed; for now only
        objects inheriting one of the catalog mixin classes are considered """
    return isinstance(obj, CatalogMultiplex) or \
        isinstance(obj, CMFCatalogAware)


class RequestFactory(object):
    implements(IRequestFactory)

    def getRequests(self):
        "factory method"
        return requests

    def save(self, values):
        self._loadConfig()
        logger.info("Posting document to %s \n%s"% (self.post_url, json.dumps(values)))
        res = self.getRequests().post(self.post_url, json.dumps(values))
        if (res.status_code != 200):
            logger.error("Posting document to %s produced error: %d\n%s" % 
                    (self.post_url, res.status_code, res.content))
            raise Exception("Posting document failed, will not continue: %d " % res.status_code)

    def delete(self, values):
        """Deletes a document, values: the document dict"""
        self._loadConfig()

        self.delete_url = self.post_url[:-3] + unicode(values['id'])
        logger.info("DELETE to %s"% (self.delete_url))

        res = self.getRequests().delete(self.delete_url)
        if (res.status_code != 200):
            logger.error("DELETE to %s produced error: %d\n%s" % 
                    (self.delete_url, res.status_code, res.content))
            raise Exception("Posting document failed, will not continue: %d " % res.status_code)

    def _loadConfig(self):
        config = queryUtility(IZeroCMSSettings)
        if config is not None:
            self.post_url = config.getConfig()['post_url']
        else:
            raise Exception("No config defined.")



class ZeroCMSIndexProcessor(object):
    """ a queue processor for zerocms """
    implements(IZeroCMSIndexQueueProcessor)

    def __init__(self, requestFactory=None):
        logger.info("Starting Zeo procesor")
        self.requestFactory = requestFactory
    def getRequestFactory(self):
        if self.requestFactory is None:
            self.requestFactory = getUtility(IRequestFactory)
        return self.requestFactory

    def begin(self):
        """ called before processing of the queue is started """
        pass

    def commit(self):
        """ called after processing of the queue has ended """
        pass

    def abort(self):
        """ called if processing of the queue needs to be aborted """
        pass

    def loadConfig(self):
        self.config = queryUtility(IZeroCMSSettings).getConfig()
        logger.info("Got config: " + repr(self.config) ) 

    def index(self, obj, attributes=None):
        logger.info("Index called: ")
        data = self.makeData(obj)
        #print "Got data: \n%s" % repr(data)
        self.getRequestFactory().save(data)

        return
    def reindex(self, obj, attributes=None):
        self.index(obj, attributes)


    def unindex(self, obj):
        logger.info("Unindex called")
        #print "Got data: \n%s" % repr(data)
        data = self.makeData(obj)
        self.getRequestFactory().delete(data)

    def makeData(self, obj):
        "Calld by inded and unindex to get the document"
        self.loadConfig()

        mapper = DataMapper(self.config['instance_id'],
                self.config['instance_url'])
        
        return mapper.convert(self.wrapObject(obj), obj.__class__.__name__)
       

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

