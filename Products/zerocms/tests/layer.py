# -*- coding: utf-8

# Plone imports -> PloneTestCase load zcml layer and install product
from Products.PloneTestCase import ptc
import collective.testcaselayer.ptc


ptc.setupPloneSite()

class ZeroCMSLayer(collective.testcaselayer.ptc.BasePTCLayer):
    def afterSetUp(self):
        "setup product"
        self.addProfile('Products.zerocms:default')


Layer = ZeroCMSLayer([collective.testcaselayer.ptc.ptc_layer])

