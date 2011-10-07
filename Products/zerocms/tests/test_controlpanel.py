# -*- coding: utf-8
import os, sys, datetime, unittest
from Products.PloneTestCase import ptc
from zope.component import getMultiAdapter
from plone.registry import Registry
from Products.CMFCore.utils import getToolByName

from Products.zerocms.interfaces import IZeroCMSSettings
from Products.zerocms.tests.layer import Layer

class RegistryTest(ptc.PloneTestCase):

    layer = Layer

    def afterSetUp(self):
        # Set up the zerocms settings registry
        self.loginAsPortalOwner()
        self.registry = Registry()
        self.registry.registerInterface(IZeroCMSSettings)

    def test_zerocms_controlpanel_view(self):
        view = getMultiAdapter((self.portal, self.portal.REQUEST), 
                               name="zerocms-settings")
        view = view.__of__(self.portal)
        self.failUnless(view())

    def test_zerocms_controlpanel_view_protected(self):
        from AccessControl import Unauthorized
        self.logout()
        self.assertRaises(Unauthorized,
                          self.portal.restrictedTraverse,
                         '@@zerocms-settings')

    def test_record_zerocms_key(self):
        # Test that the zerocms_key record is in the control panel
        record_post_url = self.registry.records[
            'collective.zerocms.interfaces.IZeroCMSSettings.post_url']
        self.failUnless('post_url' in IZeroCMSSettings)
        self.assertEquals(record_post_url.value, u"")

    def test_record_instance_url(self):
        record_instance_url = self.registry.records[
            'collective.zerocms.interfaces.IZeroCMSSettings.instance_url']        
        self.failUnless('instance_url' in IZeroCMSSettings)
        self.assertEquals(record_instance_url.value, u"")

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

