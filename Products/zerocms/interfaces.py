# -*- coding: utf-8
from zope.interface import Interface

class IZeroCMS(Interface):
    ''' Interface for ZeroCMS
    '''


class IZeroCMSSettings(Interface):
    """Global ZeroCMS settings
       @author: Tarjei Huse (tarjei@scanmine.com)
       """

    post_url = schema.TextLine(title=_(u"Url to post documents"),
                                  description=_(u"ZeroCMS post url",
                                                default="http://localhost/ZeroCMS"),
                                  required=true,
                                  default=u'http://localhost/ZeroCMS',)

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
