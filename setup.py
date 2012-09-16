#!/usr/bin/env python
from distutils.core import setup

setup(name='frozn',
        version='0.0.3',
        description='An app for generating static blogs',
        author='Jason Bartz',
        author_email='jason@jasonbartz.com',
        url='https://github.com/jasonbartz/frozn',
        packages = ['frozn','frozn.builder'],
        license = 'MIT',
        package_data = {'': [
            'static/*.js',
            'static/*.css',
            'static/prettify/*.js',
            'static/prettify/*.css',
            'templates/*.html',
        ]},
        classifiers=[
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Utilities'
        ],
)