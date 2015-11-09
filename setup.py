#!/usr/bin/env python
"""
Install wagtailnews using setuptools
"""
import sys

with open('wagtailnews/version.py', 'r') as f:
    version = None
    exec(f.read())

with open('README.rst', 'r') as f:
    readme = f.read()

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


install_requires = ['wagtail>=1.0']
if sys.version_info < (3,):
    install_requires += ['enum34==1.0.4']

setup(
    name='wagtailnews',
    version=version,
    description='News / blog plugin for the Wagtail CMS',
    long_description=readme,
    author='Tim Heap',
    author_email='tim@takeflight.com.au',
    url='https://bitbucket.org/takeflight/wagtailnews',

    install_requires=install_requires,
    zip_safe=False,
    license='BSD License',

    packages=find_packages(),

    include_package_data=True,
    package_data={},

    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
    ],
)
