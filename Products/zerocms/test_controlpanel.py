# -*- coding: utf-8
import os, sys, datetime
"""
TODO!
class RegistryTest(PloneTestCase):

    layer = AkismetLayer

    def afterSetUp(self):
        # Set up the akismet settings registry
        self.loginAsPortalOwner()
        self.registry = Registry()
        self.registry.registerInterface(IAkismetSettings)

     def test_akismet_controlpanel_view(self):
        view = getMultiAdapter((self.portal, self.portal.REQUEST), 
                               name="akismet-settings")
        view = view.__of__(self.portal)
        self.failUnless(view())

    def test_akismet_controlpanel_view_protected(self):
        from AccessControl import Unauthorized
        self.logout()
        self.assertRaises(Unauthorized,
                          self.portal.restrictedTraverse,
                         '@@akismet-settings')

    def test_record_akismet_key(self):
        # Test that the akismet_key record is in the control panel
        record_akismet_key = self.registry.records[
            'collective.akismet.interfaces.IAkismetSettings.akismet_key']
        self.failUnless('akismet_key' in IAkismetSettings)
        self.assertEquals(record_akismet_key.value, u"")

    def test_record_akismet_key_site(self):
        record_akismet_key_site = self.registry.records[
            'collective.akismet.interfaces.IAkismetSettings.akismet_key_site']        
        self.failUnless('akismet_key_site' in IAkismetSettings)
        self.assertEquals(record_akismet_key_site.value, u"")

    def test_suite():
        return unittest.defaultTestLoader.loadTestsFromName(__name__)

"""
