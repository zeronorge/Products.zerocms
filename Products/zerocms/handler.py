# -*- coding: utf-8
import os, sys, datetime, time
from five import grok
from zope.app.container.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent, IObjectModifiedEvent, IObjectRemovedEvent
from Products.ATContentTypes.content.document import ATDocument
import requests, json, StringIO

from zope.component import getUtility
from plone.registry.interfaces import IRegistry


event_stats = {'create': 0, 'update': 0, 'delete' :0}

def get_invoke_count(stat):
    return event_stats[stat]

def reset_invoke_count():
    event_stats = {'create': 0, 'update': 0, 'delete' :0}
    

_UPDATER=ZeroCMSDocumentUpdater({})

@grok.subscribe(ATDocument, IObjectCreatedEvent)
def create(event, other):
    _UPDATER.create(event, other)
    print "\n\n----------> create called <-------------"
    event_stats['create'] += 1

@grok.subscribe(ATDocument, IObjectModifiedEvent)
def update(event, other):
    "update event"
    _UPDATER.update(event, other)
    print "\n\n----------> update called <-------------"
    event_stats['update'] += 1


@grok.subscribe(ATDocument, IObjectRemovedEvent)
def delete(event, other):
    "delete event"
    _UPDATER.delete(event, other)
    print "\n\n----------> delete called <-------------"
    event_stats['delete'] += 1



class DocumentUpdater(object):

    def update_config(self, config):
        self.config = {'post_url': 'http://localhost/ZeroCMS/document/add', 'instance_id': 'zero', 'instance_url': 'http://test.zero.no'}

        for key in [ "post_url", "instance_id", "instance_url"]:
            if key in config:
                self.config[key] = config[key]

class ZeroCMSDocumentUpdater(DocumentUpdater):
    def __init__(self, config):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IZeroCMSSettings)

        self.config['post_url'] = settings.post_url
        self.config['instance_url'] = settings.instance_url
        self.config['instance_id'] = settings.instance_id

        self.update_config(config)

    def create(self, event):
        print "Event create called with event: "
        print repr(event)

    def update(self, doc):
        """
        Posts an updated document to the document repository
        """
        result = self.do_post(self.config['post_url'], self.encode_document(doc))

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

