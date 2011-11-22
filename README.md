Introduction
============

This is a Product to update Plone documents to ZeroCMS. 

A lot of the code is has been imported and modified from collective.solr. 

http://plone.org/products/collective.solr

To run reindex:
http://localhost:7070/zerorally/@@zerocms-maintenance/reindex




## To install:

Add to your buildout:



### To run tests:

Install buildout:
    apt-get install python-zc.buildout

Run buildout:
    buildout ./buildout.cfg

Use the testrunner from your plone instance:

../../bin/test Products.zerocms


