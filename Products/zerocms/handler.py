# -*- coding: utf-8
import os, sys, datetime, time

import requests, json, StringIO


class DocumentUpdater(object):

    def update_config(self, config):
        self.config = {'post_url': 'http://localhost/ZeroCMS/document/add', 'instance_id': 'zero', 'instance_url': 'http://test.zero.no'}

        for key in [ "post_url", "instance_id", "instance_url"]:
            if key in config:
                self.config[key] = config[key]

class NullHandler(object):
    "A nullobject to safisfy actions when no object exists"
    def create(self, event, other):
        pass

    def update(self, doc):
        pass

    def delete(self, event, other):
        pass

class DebugHandler(object):

    def create(self, event, other):
        print "Event create called with event: "
        print repr(event)
        print repr(other)

    def update(self, doc):
        """
        Posts an updated document to the document repository
        """
        print "Event update called with event: "
        print repr(event)
        print repr(other)


    def delete(self, event, other):
        print "\n\n----------> update called with args: <-------------"
        print repr(event)
        print repr(other)
        print "\n\n"


class ZeroCMSDocumentUpdater(DocumentUpdater):
    def __init__(self, config):
        self.update_config(config)

    def create(self, event, other):
        print "Event create called with event: "
        print repr(event)
        print repr(other)

    def update(self, doc):
        """
        Posts an updated document to the document repository
        """
        result = self.do_post(self.config['post_url'], self.encode_document(doc))

    def delete(self, event, other):
        pass

    def do_post(url, data):
        "Posts the string to the url"
        #requests.settings.verbose = sys.stderr
        return requests.post(url, data)

    
    def encode_document(self, doc):
        "converts the document to a json encoded string with all "
        ret = {'dokumentID': "",
                'ID': "",
                'type': "",
                'body': "",
                'author': "",
                'dateCreated': "",
                'dateUpdated': "",
                'url': "",
                'title': "",
                'source': "",
                'tags': []
        }

        return json.dumps(ret)



    


class LoggingDocumentUpdater(DocumentUpdater):
    ''' This class only logs the requests to file for debugging'''
    def __init__(self, config):
        self.update_config(config)
        self.file_name = "/tmp/DocumentUpdaterLog-%d" % (time.time())
        self.file_handle = open(self.file_name, "w")
        
    def update(self, doc):
        self.log_input(doc, "update")

    def log_input(self, doc, caller):
        s = repr(doc)
        self.file_handle.write("%s called:\n" % caller)
        self.file_handle.write(s)

    def created(self, doc):
        self.log_input(doc, "created")
    def deleted(self, doc):
        self.log_input(doc, "deleted")

