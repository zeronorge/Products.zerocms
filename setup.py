from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='Products.zerocms',
      version=version,
      description="zerocms import/export product",
      long_description=open("README.md").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Tarjei Huse',
      author_email='tarjei@scanmine.com',
      url='http://github.com/zeronorge/Products.zerocms/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'requests', 'five.grok',
          # -*- Extra requirements: -*-
                  'Acquisition',
        'archetypes.schemaextender',
        'collective.indexing >= 2.0a2',
        'DateTime',
        'Plone >= 4.1',
        'plone.app.content',
        'plone.app.controlpanel',
        'plone.app.registry',
        'plone.app.layout',
        'plone.indexer',
        'Products.Archetypes',
        'Products.CMFCore',
        'Products.CMFDefault',
        'Products.GenericSetup',
        'setuptools',
        'transaction',
        'ZODB3',
        'zope.component',
        'zope.formlib',
        'zope.interface',
        'zope.publisher',
        'zope.schema',
        'Zope2 >= 2.13',
      ],
        extras_require = {'test': [
        'cElementTree',
        'collective.testcaselayer',
        'Products.LinguaPlone >=3.1a1',
        'Products.PloneTestCase',
      ]},

      entry_points="""
      # -*- Entry points: -*-
      """,
      )
