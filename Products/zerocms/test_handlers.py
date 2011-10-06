
# Zope imports
import unittest
from handlers import *

import requests, StringIO, json

class TestSolrUpdater(unittest.TestCase):
    def test_init(self):
        assert(False)

class TestLoggingDocumentUpdater(unittest.TestCase):

    def test_init(self):
        df = LoggingDocumentUpdater({'post_url': "test"})
        self.assertEquals(df.config['post_url'], "test")
        self.assertEquals(df.config['instance_id'], "zero")

    def test_file_gets_set_up(self):
        df = LoggingDocumentUpdater({'post_url': "test"})
        self.assertTrue(df.file_handle)
    
    def test_store_doc(self):
        df = LoggingDocumentUpdater({'post_url': "test"})
        df.file_handle = StringIO.StringIO()

        df.update({'test' : 'rest'})

        self.assertEquals("update called:\n{'test': 'rest'}", df.file_handle.getvalue())



