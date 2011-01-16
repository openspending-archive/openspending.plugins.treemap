from setuptools import setup, find_packages
import sys, os

from wdmmgext.treemap import __version__

setup(name='wdmmg-treemap',
      version=__version__,
      description="Where Does My Money Go? Treemap Visualizations",
      long_description="",
      classifiers=[], 
      keywords='wdmmg treemap',
      author='Open Knowledge Foundation',
      author_email='info@okfn.org',
      url='http://www.okfn.org',
      license='GPL v3',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      namespace_packages=['wdmmgext'],
      zip_safe=False,
      message_extractors = {
            'wdmmgext/treemap': [
                ('**.py', 'python', None)
                ],
            'theme': [
                ('templates/**.html', 'genshi', None),
                ('public/**', 'ignore', None)
                ],
            },
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      
      [wdmmg.plugins]
      treemap = wdmmgext.treemap:TreemapGenshiStreamFilter
      """,
      )
