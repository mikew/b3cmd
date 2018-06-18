#!/usr/bin/env python

from __future__ import with_statement

# import sys

from setuptools import setup, find_packages

# from fabric.version import get_version


# with open('README.rst') as f:
    # readme = f.read()

# long_description = """
# To find out what's new in this version of Fabric, please see `the changelog
# <http://fabfile.org/changelog.html>`_.

# You can also install the `in-development version
# <https://github.com/fabric/fabric/tarball/master#egg=fabric-dev>`_ using
# pip, with `pip install fabric==dev`.

# ----

# %s

# ----

# For more information, please see the Fabric website or execute ``fab --help``.
# """ % (readme)

# if sys.version_info[:2] < (2, 6):
    # install_requires=['paramiko>=1.10,<1.13']
# else:
    # install_requires=['paramiko>=1.10']

from b3cmd import __version_string__

setup(
    name='b3cmd',
    version=__version_string__,
    description='',
    long_description='',
    author='Mike Wyatt',
    author_email='wyatt.mike@gmail.com',
    url='',
    packages=find_packages(),
    test_suite='nose.collector',
    tests_require=('nose',),
    install_requires=(
        'Fabric>=1.10.2, <2.0',
        'click>=5.1',
    ),
    entry_points={
        'console_scripts': [
            'b3cmd = b3cmd.cli:main',
        ]
    },
    classifiers=(),
    package_data={
        'b3cmd.contrib': [
            'completion.sh'
        ]
    }
)
