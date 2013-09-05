#!/usr/bin/env python

import os
import sys
import fnmatch
import subprocess

## prepare to run PyTest as a command
from distutils.core import Command

from setuptools import setup, find_packages

from version import get_git_version
VERSION = get_git_version()
PROJECT = 'dblogger'
URL = 'tbd'
AUTHOR = 'Diffeo, Inc.'
AUTHOR_EMAIL = 'support@diffeo.com'
DESC = 'DB-backed python logging.Handler subclass that uses kvlayer, and provides command-line tools.'


def read_file(file_name):
    file_path = os.path.join(
        os.path.dirname(__file__),
        file_name
    )
    return open(file_path).read()


def recursive_glob(treeroot, pattern):
    results = []
    for base, dirs, files in os.walk(treeroot):
        goodfiles = fnmatch.filter(files, pattern)
        results.extend(os.path.join(base, f) for f in goodfiles)
    return results


class InstallTestDependencies(Command):
    '''install test dependencies'''

    description = 'installs all dependencies required to run all tests'

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def easy_install(self, packages):
        cmd = ['easy_install']
        if packages:
            cmd.extend(packages)
            errno = subprocess.call(cmd)
            if errno:
                raise SystemExit(errno)

    def run(self):
        if self.distribution.install_requires:
            self.easy_install(self.distribution.install_requires)
        if self.distribution.tests_require:
            self.easy_install(self.distribution.tests_require)


class PyTest(Command):
    '''run py.test'''

    description = 'runs py.test to execute all tests'

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        if self.distribution.install_requires:
            self.distribution.fetch_build_eggs(
                self.distribution.install_requires)
        if self.distribution.tests_require:
            self.distribution.fetch_build_eggs(
                self.distribution.tests_require)

        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)

setup(
    name=PROJECT,
    version=VERSION,
    description=DESC,
    long_description=read_file('README.rst'),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    packages=find_packages('src', exclude=('tests', 'tests.*')),
    package_dir={'': 'src'},
    cmdclass={'test': PyTest,
              'install_test': InstallTestDependencies},
    # We can select proper classifiers later
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',  ## MIT/X11 license http://opensource.org/licenses/MIT
    ],
    tests_require=[
        'pytest',
        'ipdb',
        'pytest-cov',
        'pytest-xdist',
        'pytest-timeout',
        'pytest-incremental',
        'pytest-capturelog',
        'epydoc',
    ],
    install_requires=[
        'kvlayer',
        'test-uuid'
    ],
)
