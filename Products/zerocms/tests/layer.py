# -*- coding: utf-8

# Plone imports -> PloneTestCase load zcml layer and install product
from Products.PloneTestCase import ptc
import collective.testcaselayer.ptc
from Testing.ZopeTestCase import Sandboxed
from Products.CMFPlone.utils import _createObjectByType
from Testing.ZopeTestCase import installPackage, installProduct
from Zope2.App import zcml

ptc.setupPloneSite()

class ZeroCMSLayer(collective.testcaselayer.ptc.BasePTCLayer):
    def afterSetUp(self):
        from collective import indexing
        from Products import zerocms
        zcml.load_config('configure.zcml', indexing)
        zcml.load_config('configure.zcml', zerocms)
        installPackage('collective.indexing', quiet=True)
        installPackage('Products.zerocms', quiet=True)
        # account for difference in default content in Plone 4.0 / 4.1
        #_createObjectByType('Document', self.portal.events, 'previous')
        self.addProfile('Products.zerocms:default')


class ZeroCMSTestCase(Sandboxed,ptc.PloneTestCase):
    layer = ZeroCMSLayer([collective.testcaselayer.ptc.ptc_layer])

    def afterSetUp(self):
        "setup product"


