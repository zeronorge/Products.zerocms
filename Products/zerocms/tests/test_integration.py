from unittest import defaultTestLoader

# test-specific imports go here...
from zope.component import queryUtility, getUtilitiesFor, provideUtility
from Products.CMFCore.utils import getToolByName
from collective.indexing.interfaces import IIndexQueueProcessor
from Products.zerocms.interfaces import IZeroCMSIndexQueueProcessor, IRequestFactory, IZeroCMSSettings

#from collective.solr.interfaces import ISolrConnectionConfig
#from collective.solr.interfaces import ISolrConnectionManager
#from collective.solr.exceptions import SolrInactiveException
#from collective.solr.tests.utils import getData, fakehttp, fakeServer
from mockito import *
from transaction import commit
from socket import error, timeout
from time import sleep

from layer import ZeroCMSTestCase

from Products.zerocms.mapper import DataMapper, requiredAttributes 

class IndexingTests(ZeroCMSTestCase):

    def save(self, data):
        print "save(): data recived: " + repr(data)
        self.savedData = data

    def afterSetUp(self):
        self.savedData = None
        self.folder.unmarkCreationFlag()    # stop LinguaPlone from renaming
        self.config = queryUtility(IZeroCMSSettings)
        self.config.instance_id = "test_"
        self.config.instance_url= "http://test.com"
        self.factory = queryUtility(IRequestFactory)
        if self.factory is None:
            raise Exception("No factory created")
        self.factory.save= self.save
        self.expData = '{"locallyAllowedTypes": [], "description": "", "language": "en", "title": "Foo", "rights": "", "id": "test_user_1_", "contributors": [], "immediatelyAddableTypes": [], "creators": [], "constrainTypesMode": -1, "subject": []}'

    def beforeTearDown(self):
        pass


    def testIndexObject(self):
        self.folder.processForm(values={'title': 'Foo'})    # updating sends
        self.assertEquals(self.folder.Title(), 'Foo')
        commit()                        # indexing happens on commit
        self.assertEqual(self.folder.Title(), 'Foo')
        self.assertTrue(self.savedData is not None)
        # 37 UUID + 5 instance_id
        self.assertEquals(len(self.savedData['ID']) ,42)
        self.assertEquals(self.savedData['url'] ,  "http://test.com/plone/Members/test_user_1_")

        for item in requiredAttributes:
            self.assertTrue(item in self.savedData, msg="Missing %s in saved data" % item)

        self.assertNotEquals(self.savedData['body'], "")

    def _test_callIndexing(self):
        indexProcessor = queryUtility(IZeroCMSIndexQueueProcessor, name="zerocms")
        indexProcessor.index(self.folder, attributes = {'url' : 'test'})

        self.assertEquals(len(self.savedData['ID']) ,36)

    def _testNoIndexingWithMethodOverride(self):
        self.setRoles(['Manager'])
        output = []
        connection = self.proc.getConnection()
        responses = [getData('dummy_response.txt')] * 42
        output = fakehttp(connection, *responses)
        self.folder.invokeFactory('Topic', id='coll', title='a collection')
        self.folder.coll.addCriterion('Type', 'ATPortalTypeCriterion')
        self.assertTrue('crit__Type_ATPortalTypeCriterion' not in str(output))
        commit()
        self.assert_(repr(output).find('a collection') > 0,
            '"title" data not found')
        self.assert_(repr(output).find('crit') == -1, 'criterion indexed?')
        objs = self.portal.portal_catalog(portal_type='ATPortalTypeCriterion')
        self.assertEqual(list(objs), [])
        self.folder.manage_delObjects('coll')

    def _testNoIndexingForNonCatalogAwareContent(self):
        self.setRoles(['Manager'])
        output = []
        ref = self.folder.addReference(self.portal.news, 'referencing')
        self.folder.processForm(values={'title': 'Foo'})
        commit()                        # indexing happens on commit
        self.assertTrue(self.savedData is None)

class UtilityTests(ZeroCMSTestCase):

    def testGenericInterface(self):
        proc = queryUtility(IIndexQueueProcessor, name='zerocms')
        self.failUnless(proc, 'utility not found')
        self.failUnless(IIndexQueueProcessor.providedBy(proc))
        self.failUnless(IZeroCMSIndexQueueProcessor.providedBy(proc))

    def testGetRequestFactory(self):
        proc = queryUtility(IRequestFactory)
        self.failUnless(proc, 'request factory utility not found')

    def testSolrInterface(self):
        proc = queryUtility(IZeroCMSIndexQueueProcessor, name='zerocms')
        self.failUnless(proc, 'utility not found')
        self.failUnless(IIndexQueueProcessor.providedBy(proc))
        self.failUnless(IZeroCMSIndexQueueProcessor.providedBy(proc))

    def testRegisteredProcessors(self):
        procs = list(getUtilitiesFor(IIndexQueueProcessor))
        self.failUnless(procs, 'no utilities found')
        zerocms = queryUtility(IZeroCMSIndexQueueProcessor, name='zerocms')
        self.failUnless(zerocms in [util for name, util in procs],
            'zerocms utility not found')

#    def testSearchInterface(self):
#        search = queryUtility(ISearch)
#        self.failUnless(search, 'search utility not found')
#        self.failUnless(ISearch.providedBy(search))


def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)
    #return defaultTestLoader.loadTestsFromTestCase(UtilityTests)
