# -*- coding: utf-8
import os, sys, datetime, time
from five import grok
from zope.app.container.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent, IObjectModifiedEvent, IObjectRemovedEvent
from Products.ATContentTypes.content.document import ATDocument
import requests, json, StringIO

from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from handler import ZeroCMSDocumentUpdater, NullHandler
from interfaces import IZeroCMSSettings


module_config = {
    'event_handler_factory': None
}
event_stats = {'create': 0, 'update': 0, 'delete' :0}

def get_invoke_count(stat):
    return event_stats[stat]

def reset_invoke_count():
    event_stats = {'create': 0, 'update': 0, 'delete' :0}

def create_handler():
    "setup ZeroCMSDocumentUpdater with config from registry"
    registry = getUtility(IRegistry)
    if not 'Products.zerocms.interfaces.IZeroCMSSettings.post_url' in registry:
        print "no handler defined no action will happen"
        return NullHandler()
    else:
        handler = ZeroCMSDocumentUpdater({})
        settings = registry.forInterface(IZeroCMSSettings)
        handler.config['post_url'] = settings.post_url
        handler.config['instance_url'] = settings.instance_url
        handler.config['instance_id'] = settings.instance_id
        return handler

module_config['event_handler_factory'] = create_handler

def set_event_handler_factory(handler):
    "sets the functionpointer used to create eventhandlers. Usefull for injecting mocks"
    module_config['event_handler_factory'] = handler

@grok.subscribe(ATDocument, IObjectAddedEvent)
def create(document, event_type):
    handler = module_config['event_handler_factory']()
    handler.create(document, event_type)
#    print "\n\n----------> create (%s, %s) called <-------------" % (type(document).__name__, type(event_type).__name__)
    event_stats['create'] += 1

@grok.subscribe(ATDocument, IObjectModifiedEvent)
def update(document, event_type):
    "update event"
    handler = module_config['event_handler_factory']()
    handler.update(document, event_type)
#    print "\n\n----------> update called <-------------"
    event_stats['update'] += 1


@grok.subscribe(ATDocument, IObjectRemovedEvent)
def delete(document, event_type):
    "delete event"
    handler = module_config['event_handler_factory']()
    handler.delete(document, event_type)
#   print "\n\n----------> delete called <-------------"
#    print repr(document)
    event_stats['delete'] += 1


