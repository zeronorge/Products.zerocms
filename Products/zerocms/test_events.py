
# Zope imports
from Testing import ZopeTestCase
import unittest

# Plone imports -> PloneTestCase load zcml layer and install product
from Products.PloneTestCase import PloneTestCase

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

PloneTestCase.setupPloneSite(products=['Products.zerocms'])

from events import get_invoke_count, reset_invoke_count
import requests, StringIO, json

class TestEventHandling(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        reset_invoke_count()
        

    def test_document_updated(self):
        df = ZeroCMSDocumentUpdater({})

    def test_encode_document(self):
        df = ZeroCMSDocumentUpdater({})

        json_encoded_string = df.encode_document({})
        doc = json.loads(json_encoded_string)
        self.assertEquals(doc['dokumentID'], "")

    def test_create_document(self):
        self.folder.invokeFactory("Document", id="test")
        print repr(self.folder.test)
        self.assertEquals(1, get_invoke_count("create"))


