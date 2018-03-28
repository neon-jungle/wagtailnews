#!/usr/bin/env python
"""
Install wagtailnews using setuptools
"""
from setuptools import find_packages, setup

with open('wagtailnews/version.py', 'r') as f:
    version = None
    exec(f.read())

with open('README.rst', 'r') as f:
    readme = f.read()

# Documentation dependencies
documentation_extras = [
    'Sphinx>=1.4.6',
    'sphinx-autobuild>=0.5.2',
    'sphinx_rtd_theme>=0.1.8',
    'sphinxcontrib-spelling==2.1.1',
    'pyenchant==1.6.6',
]

setup(
    name='wagtailnews',
    version=version,
    description='News / blog plugin for the Wagtail CMS',
    long_description=readme,
    author='Tim Heap',
    author_email='tim@takeflight.com.au',
    url='https://github.com/takeflight/wagtailnews/',

    install_requires=[
        'wagtail>=2.0.0',
    ],
    extras_require={
        'docs': documentation_extras
    },
    zip_safe=False,
    license='BSD License',

    packages=find_packages(exclude=['tests*']),

    include_package_data=True,
    package_data={},

    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
    ],
)
