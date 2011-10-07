# -*- coding: utf-8
from Products.Archetpes.atapi import ObjectField, StringField, FileField, TextField, DateTimeField, LinesField, IntegerField, FloatField, FixedPointField, ReferenceField, ComputedField, BooleanField, CMFObjectField, Image, ImageField

class Datamapper(object):
    implements(IDataMapper)

    def __init__(self):
        self.conversionMap= {
                "DateTime": 
        }
