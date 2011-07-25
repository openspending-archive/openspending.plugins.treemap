from setuptools import setup, find_packages
from treemap import __version__

setup(
    name='openspending.plugins.treemap',
    version=__version__,
    description='OpenSpending Treemap Visualizations',
    keywords='openspending openspending-plugin treemap visualisation',
    author='Open Knowledge Foundation',
    author_email='okfn-help at lists okfn org',
    url='http://github.com/okfn/openspending.plugins.treemap',
    license='GPL v3',
    install_requires=[
        'openspending'
    ],
    packages=find_packages('.packageroot'),
    package_dir={'': '.packageroot'},
    namespace_packages=['openspending', 'openspending.plugins'],
    package_data={
        'openspending.plugins.treemap': [
            'public/js/*.js'
        ]
    },
    entry_points={
        'openspending.plugins': [
            'treemap = openspending.plugins.treemap:TreemapPlugin'
        ]
    },
    zip_safe=False
)
