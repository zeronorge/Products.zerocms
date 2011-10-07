from logging import getLogger
import json
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
IZeroCMSSettings)

logger = getLogger('Products.zerocms.indexer')


def indexable(obj):
    """ indicate whether a given object should be indexed; for now only
        objects inheriting one of the catalog mixin classes are considered """
    return isinstance(obj, CatalogMultiplex) or \
        isinstance(obj, CMFCatalogAware)


def datehandler(value):
    # TODO: we might want to handle datetime and time as well;
    # check the enfold.solr implementation
    if value is None:
        raise AttributeError
    if isinstance(value, str) and not value.endswith('Z'):
        value = DateTime(value)
    if isinstance(value, DateTime):
        v = value.toZone('UTC')
        value = '%04d-%02d-%02dT%02d:%02d:%06.3fZ' % (v.year(),
            v.month(), v.day(), v.hour(), v.minute(), v.second())
    elif isinstance(value, date):
        # Convert a timezone aware timetuple to a non timezone aware time
        # tuple representing utc time. Does nothing if object is not
        # timezone aware
        value = datetime(*value.utctimetuple()[:7])
        value = '%s.%03dZ' % (value.strftime('%Y-%m-%dT%H:%M:%S'), value.microsecond % 1000)
    return value



handlers = {
    'DateTimeField': datehandler 
}


def boost_values(obj, data):
    """ calculate boost values using a method or skin script;  returns
        a dictionary with the values or `None` """
    boost_index_getter = aq_get(obj, 'solr_boost_index_values', None)
    if boost_index_getter is not None:
        return boost_index_getter(data)

class DataManager(object):

    

    def __init__(self):
        self.requiredAttributes ={
            'dokumentID': "",
                'ID': "",
                'type': "",
                'body': "",
                'author': "",
                'dateCreated': "",
                'dateUpdated': "",
                'url': "",
                'title': "",
                'source': "",
                'tags': []
        }

    def convert(self, obj):
        data = self.getData(obj)

        # cleanup data

        data['ID'] = data['id']
        del(data['id'])

        data['ID'] = obj.UID
        print repr(obj.contributors)
        data['type'] = obj.__class__.__name__
        data['url'] = '/'.join(obj.getPhysicalPath())

        data['dateCreated'] = obj.created().ISO8601()
        data['dateUpdated'] = obj.modified().ISO8601()

#        self.copyAndDel(data,"create", "dateCreated")
#        self.copyAndDel(data,"create", "dateUpdated")
#        self.copyAndDel(data,"create", "contributors")


        for key in self.requiredAttributes.keys():
            if not key in data:
                print "Missing item: %s"% key
        for key in data.keys():
            if key not in self.requiredAttributes.keys():
                print "K :"  + key
        return data

    def copyAndDel(self, data, _from, _to):
        data[_to] = data[_from]
        del(data[_from])

    def getData(self, obj):
        schema = obj.schema
        if schema is None:
            print "no schema defined"
            logger.warn("No schema defined for object: " +
                    repr(obj))
            return {}, ()
        attributes = schema.keys()
        data, marker = {}, []
        for name in attributes:
            try:
                value = getattr(obj, name)
                if callable(value):
                    value = value()
            except ConflictError:
                raise
            except AttributeError:
                continue
            except Exception:
                logger.exception('Error occured while getting data for '
                    'indexing!')
                continue
            if not isinstance(value, (str, int,
                    tuple,unicode)):
                _type = type(value)
                className = None
                if (_type == 'instance'):
                    className = value.__class__.__name__

                if _type == 'instance' and \
                          className in handlers:
                    value = mapper[className]()

                    print "converted %s: %s %s" %(name,
                            value,className)
                else:
                    if className is None:
                        logger.warn("Unindexed type: %s" % type(name).__name__)
                    else:
                        logger.warn("Unindexed type: %s" %
                                className)
                    continue

            if value is not None:
                data[name] = value
        #missing = set(schema.requiredFields) - set(data.keys())
        return data



class RequestFactory(object):
    implements(IRequestFactory)

    def __init__(self):
        config = queryUtility(IZeroCMSSettings)
        if config is not None:
            self.post_url = config.post_url

    def save(self, values):
        requests.post(self.post_url, json.dumps(values))


class ZeroCMSIndexProcessor(object):
    """ a queue processor for zerocms """
    implements(IZeroCMSIndexQueueProcessor)

    def __init__(self, requestFactory=None):
        self.requestFactory = requestFactory
        if requestFactory is None:
            self.requestFactory = getUtility(IRequestFactory)

    def index(self, obj, attributes=None):
        print "Index called: " + repr(obj)

        mapper = DataManager()
        

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

    def begin(self):
        pass

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

    def getData(self, obj, attributes=None):

        schema = obj.schema

        if schema is None:
            print "no schema defined"
            return {}, ()
        if attributes is None:
            attributes = schema.keys()
        obj = self.wrapObject(obj)
        data, marker = {}, []
        for name in attributes:
            try:
                value = getattr(obj, name)
                if callable(value):
                    value = value()
            except ConflictError:
                raise
            except AttributeError:
                continue
            except Exception:
                logger.exception('Error occured while getting data for '
                    'indexing!')
                continue
            if not isinstance(value, (str, int,
                    tuple,unicode)):
                _type = type(value)
                className = None
                if (_type == 'instance'):
                    className = value.__class__.__name__

                if _type == 'instance' and \
                          className in handlers:
                    value = mapper[className]()

                    print "converted %s: %s %s" %(name,
                            value,className)
                else:
                    if className is None:
                        logger.warn("Unindexed type: %s" % type(name).__name__)
                    else:
                        logger.warn("Unindexed type: %s" %
                                className)
                    continue

            if value is not None:
                data[name] = value
        #missing = set(schema.requiredFields) - set(data.keys())
        return data, []
