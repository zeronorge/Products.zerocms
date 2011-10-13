from logging import getLogger
from persistent import Persistent
from zope.interface import implements
from zope.component import getUtility
from Products.zerocms.interfaces import IZeroCMSSchema, IZeroCMSSettings
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


class BaseZeroCMSSettings(object):
    """ utility to hold the connection configuration for the solr server """
    implements(IZeroCMSSettings)

    def __init__(self):
        self.post_url = None
        self.instance_id = None
        self.instance_url = None


class ZeroCMSSettings(BaseZeroCMSSettings, Persistent):

    def getId(self):
        """ return a unique id to be used with GenericSetup """
        return 'zerocms'


