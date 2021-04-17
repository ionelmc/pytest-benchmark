#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import io
import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


def read(*names, **kwargs):
    with io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ) as fh:
        return fh.read()


setup(
    name='pytest-benchmark',
    version='3.4.1',
    license='BSD-2-Clause',
    description='A ``pytest`` fixture for benchmarking code. It will group the tests into rounds that are calibrated to the chosen timer.',
    long_description='%s\n%s' % (
        re.compile('^.. start-badges.*^.. end-badges', re.M | re.S).sub('', read('README.rst')),
        re.sub(':[a-z]+:`~?(.*?)`', r'``\1``', read('CHANGELOG.rst'))
    ),
    author='Ionel Cristian Mărieș',
    author_email='contact@ionelmc.ro',
    url='https://github.com/ionelmc/pytest-benchmark',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Testing',
        'Topic :: System :: Benchmark',
        'Topic :: Utilities',
    ],
    project_urls={
        'Documentation': 'https://pytest-benchmark.readthedocs.io/',
        'Changelog': 'https://pytest-benchmark.readthedocs.io/en/latest/changelog.html',
        'Issue Tracker': 'https://github.com/ionelmc/pytest-benchmark/issues',
    },
    keywords=[
        'pytest', 'benchmark',
    ],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
    install_requires=[
        'pytest>=3.8',
        'py-cpuinfo',
    ],
    extras_require={
        'aspect': ['aspectlib'],
        'histogram': ['pygal', 'pygaljs'],
        ':python_version < "3.4"': ['statistics', 'pathlib2'],
        'elasticsearch': ['elasticsearch']
    },
    entry_points={
        'pytest11': [
            'benchmark = pytest_benchmark.plugin'
        ],
        'console_scripts': [
            'py.test-benchmark = pytest_benchmark.cli:main',
            'pytest-benchmark = pytest_benchmark.cli:main',
        ]
    }

)
