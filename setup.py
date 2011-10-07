from setuptools import setup, find_packages
import os

version = '1.0'

tests_require = ['collective.testcaselayer']
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
      ],
      tests_require=tests_require,
      extras_require={'tests': tests_require},
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
