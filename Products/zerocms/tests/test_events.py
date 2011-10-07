import unittest
import requests, StringIO, json


# Zope imports
from Testing import ZopeTestCase
# Plone imports -> PloneTestCase load zcml layer and install product
from Products.PloneTestCase import ptc 

# For loading zcml
#from Products.Five import zcml

## Import all module that you want load zcml
#import Products.GenericSetup
#import Products.CMFPlone
import Products.ATContentTypes

#PloneTestCase.installPackage('Products.zerocms')
#PloneTestCase.installPackage('Products.ATContentTypes')

## load zcml
#zcml.load_config('meta.zcml' , Products.CMFPlone)
#zcml.load_config('meta.zcml' , Products.GenericSetup)

from zope.component import queryUtility
from plone.registry.interfaces import IRegistry

from Products.zerocms.tests.layer import Layer
from Products.zerocms.events import get_invoke_count, reset_invoke_count, set_event_handler_factory, create_handler
from Products.zerocms.handler import ZeroCMSDocumentUpdater, DebugHandler
from Products.zerocms.interfaces import IZeroCMSSettings


class TestEventHandling(ptc.PloneTestCase):
    layer = Layer

    def afterSetUp(self):
        set_event_handler_factory(lambda : DebugHandler())
        reset_invoke_count()
        self.loginAsPortalOwner()
        registry = queryUtility(IRegistry)
        registry.registerInterface(IZeroCMSSettings)
        registry['Products.zerocms.interfaces.IZeroCMSSettings.post_url'] = u"http://localhost.com"
        registry['Products.zerocms.interfaces.IZeroCMSSettings.instance_url'] = u"http://test.com/"
        registry['Products.zerocms.interfaces.IZeroCMSSettings.instance_id'] = u"testInstance"
        
        
    def test_create_settings(self):
        handler = create_handler()
        self.assertEquals(u"testInstance", handler.config['instance_id'])
        self.assertEquals(u"http://test.com/", handler.config['instance_url'])
        self.assertEquals(u"http://localhost.com", handler.config['post_url'])

    def _test_create_document(self):
        self.folder.invokeFactory("Document", id="test")
        #print repr(self.folder.test)
        self.assertEquals(1, get_invoke_count("create"))

    def test_update_document(self):
        print repr(self.folder)
        self.folder.invokeFactory("Document", id="test2")
        self.folder.test2.text = (u"myTest")
        self.assertEquals(1, get_invoke_count("update"))

    def _test_remove_document(self):
        self.folder.invokeFactory("Document", id="test2")
        del(self.folderi['test2'])
        self.assertEquals(1, get_invoke_count("remove"))




def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

