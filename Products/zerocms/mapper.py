# -*- coding: utf-8
from Products.Archetypes.atapi import ObjectField, StringField, FileField, TextField, DateTimeField, LinesField, IntegerField, FloatField, FixedPointField, ReferenceField, ComputedField, BooleanField, CMFObjectField,  ImageField
from ZODB.POSException import ConflictError
from logging import getLogger

logger = getLogger('Products.zerocms.mapper')
"""TODO: Move DataMapper from indexer to here and """

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
requiredAttributes ={
            'documentId': "",
            'id': "",
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
class DataMapper(object):

    def __init__(self, instance_id, instance_url):
        self.instance_url = instance_url
        self.instance_id = instance_id
        self.debug = False

    def convert(self, obj, _type):
        data = self.getData(obj)

        # print "Documentid: " + data['id']
        # cleanup data
        data['documentId'] = obj.UID
        data['id'] = obj.UID + "-" + self.instance_id
        data['source'] = self.instance_id
        data['type'] = _type
        data['url'] = self.instance_url +  '/'.join(obj.getPhysicalPath())

        data['dateCreated'] = obj.created().ISO8601()
        data['dateUpdated'] = obj.modified().ISO8601()

        if not "tags" in data:
            data['tags'] = ["notTagged"]
        

        # getOwner returns plineUser
        data['author'] = obj.getOwner().getId()

#        print "author: \n" + data['author'] 
#        self.copyAndDel(data,"create", "dateCreated")
#        self.copyAndDel(data,"create", "dateUpdated")
#        self.copyAndDel(data,"create", "contributors")
        if self.debug:
            for key in requiredAttributes.keys():
                if not key in data:
                    print "Missing item: %s"% key
            for key in data.keys():
                if key not in requiredAttributes.keys():
                    print ""  + key
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
        bodyParts = []

        skipList = [
        "locallyAllowedTypes","rights","contributors","immediatelyAddableTypes","creators","constrainTypesMode"]
        for name in attributes:
            if name in skipList:
                continue
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
                        logger.warn("Unindexed type: %s = %s" % (name, type(name).__name__ ))
                    else:
                        logger.warn("Unindexed type: %s = %s" % (name, className))
                    continue
                print "%s %s" (name, className)
            # ensure we only deal with unicode attributes
            if isinstance(value, str):
                value = unicode(value) 

            if isinstance(schema[name], TextField) or isinstance(value, (unicode)):
                bodyParts.append(value)

            if value is not None:
                data[name] = value
        #missing = set(schema.requiredFields) - set(data.keys())
        if not 'body' in data:
            data['body'] = u"\n".join(bodyParts)
        return data



