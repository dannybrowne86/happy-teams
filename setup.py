#!/usr/bin/env python
from setuptools import setup, find_packages


setup(
    name='happyteams',
    version="0.0.1",
    install_requires=open('requirements.txt', 'r').read().splitlines(),
    description="A project planning and resource management application",
    author='Daniel Browne and Santiago Balestrini',
    author_email='browne.danielc@gmail.com',
    url='https://github.com/dannybrowne86/happy-teams',
    packages=find_packages(),
    license='MIT',
    platforms='any',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
    ],
    include_package_data=True,
    zip_safe=True,
    long_description=''.join(list(open('README.md', 'r'))[3:]))
