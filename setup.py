#!/usr/bin/env python

from os import path

from setuptools import setup


this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="PodcastBird657",
    version='0.0.1a3',
    description='A small podcast Wagtail app.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Oscar F',
    url='https://github.com/oscfr657/PodcastBird657',
    packages=['podcastbird657'],
    package_dir={'podcastbird657':'.'},
    package_data={'podcastbird657': [
        './migrations/*',
        './static/*/*/*',
        './static/*/*/*/*',
        './templates/*',
        './templates/*/*',
        ]
    },
    include_package_data=True,
    install_requires=[
        'django>=3.2.6',
        'wagtail>=2.14.2',
        'wagtailmedia>=0.8.0',
    ],
    license='Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Framework :: Django',
        'Framework :: Wagtail',
        'Framework :: Wagtail :: 2',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)