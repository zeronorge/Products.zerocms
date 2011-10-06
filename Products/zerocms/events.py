# -*- coding: utf-8
import os, sys, datetime, time
from five import grok
from zope.app.container.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent, IObjectModifiedEvent, IObjectRemovedEvent
from Products.ATContentTypes.content.document import ATDocument
import requests, json, StringIO

from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from handlers import *

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


