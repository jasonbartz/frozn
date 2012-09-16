#!/usr/bin/env python
from distutils.core import setup

setup(name='frozn',
        version='0.0.4',
        description='An app for generating static blogs',
        author='Jason Bartz',
        author_email='jason@jasonbartz.com',
        url='https://github.com/jasonbartz/frozn',
        packages = ['frozn'],
        license = 'MIT',
        package_data = {'': [
            'frozn_site/*.js',
            'frozn_site/*.css',
            'frozn_site/*.html',
            'frozn_site/*.json',
        ]},
        classifiers=[
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Utilities'
        ],
)