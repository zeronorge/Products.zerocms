# -*- coding: utf-8
from collective.indexing.interfaces import IIndexQueueProcessor
from zope.interface import Interface
from zope import schema
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('Products.zerocms')
class IZeroCMS(Interface):
    ''' Interface for ZeroCMS
    '''

class IZeroCMSSettings(Interface):
    """Global ZeroCMS settings
       @author: Tarjei Huse (tarjei@scanmine.com)
       """

    post_url = schema.TextLine(title=_(u"Url to post documents"),
                                  description=_(u"ZeroCMS post url",
                                                default="url.to.ZeroCMS/api/document/add"),
                                  required=True,
                                  default=u'http://localhost/ZeroCMS/api/document/add',)

    instance_url = schema.TextLine(title=_(u"Site URL"),
                                  description=_(u"ZeroCMS site url",
                                                default=u"Enter the URL to this site "),
                                  required=True,
                                  default=u'http://localhost:8080/zerorally',)
    instance_id = schema.TextLine(title=_(u"Site id"),
                                  description=_(u"id of site",
                                                default=u"Enter the URL to this site "),
                                  required=True,
                                  default=u'zerorally',)

    
class IZeroCMSIndexQueueProcessor(IIndexQueueProcessor):
    """An indexqueue handler for passing documents on to the ZeroCMS """

class IRequestFactory(Interface):
    """A simple interface for request factories"""

class IZeroCMSMaintenanceView(Interface):
    """ maintenance view for clearing, re-indexing content etc """

    def reindex(batch=1000, skip=0):
        """ find all contentish objects (meaning all objects derived from one
            of the catalog mixin classes) and (re)indexes them """
