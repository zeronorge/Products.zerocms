from logging import getLogger
from persistent import Persistent
from zope.interface import implements
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.zerocms.interfaces import IZeroCMSSettings
#from Products.zerocms.interfaces import IHTTPConnectionManager

#from Products.zerocms.solr import SolrConnection

from collective.solr.local import getLocal, setLocal

from httplib import CannotSendRequest, ResponseNotReady
from socket import error

"""

origin: collective.solr.manager
This manager only relate to a simple connection object (no commits) and is simpler in form and color than
the SolrConnectionManager.
"""

logger = getLogger('Products.zerocms.manager')
marker = object()


class ZeroCMSSettings(Persistent):
    implements(IZeroCMSSettings)

    def __init__(self):
        self.post_url = None
        self.instance_id = None
        self.instance_url = None
              
    def getConfig(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IZeroCMSSettings, check=False)

        config = {
        'post_url': settings.post_url,
        'instance_id': settings.instance_id,
        'instance_url': settings.instance_url
        }
        #logger.info("registry settings returnes " + repr(config))
        return config



    def getId(self):
        """ return a unique id to be used with GenericSetup """
        return 'zerocms'


