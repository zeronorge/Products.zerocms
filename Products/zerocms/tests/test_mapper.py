# -*- coding: utf-8
import os, sys, datetime, unittest
from Products.zerocms.mapper import *
from Products.zerocms.indexer import *
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.document import ATDocumentBase
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import KeywordWidget
from Products.Archetypes.atapi import LinesField

TestObjectSchema = ATContentTypeSchema.copy()+ Schema((
    LinesField(
        name='subject',
        widget=KeywordWidget(
            label="ZERO Tag",
            label_msgid='kortnytt_label_subject',
            i18n_domain='kortnytt',
        ),  
        accessor="Subject",
        searchable=True,
        required=True,
        multiValued=1,
    )
))



class TestObject(ATDocumentBase):
    schema = TestObjectSchema
    def __init__(self):
        pass



class DataMapperTest(unittest.TestCase):


    def setUp(self):
        self.mapper = DataMapper("zero", "http://zero.no")

    def test_checkName(self):
        self.assertEquals("tags", self.mapper.checkName("subject"))
        self.assertEquals("tags", self.mapper.checkName("tags"))

    def testGetData(self):
        indexer = ZeroCMSIndexProcessor()
        obj = TestObject()
#        obj = indexer.wrapObject(obj)
        obj.subject = ["test", "rest"]
        obj.title = u"testø".encode("utf-8")
        obj.id ="my id"
        data = self.mapper.getData(obj) 
        self.assertEquals({}, data)

