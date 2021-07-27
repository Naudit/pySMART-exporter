# Copyright (C) 2021 Rafael Leira
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# License for more details.
#
################################################################

from setuptools import setup

from distutils.core import setup
from subprocess import Popen, PIPE
import os
import re


def read_file(path):
    with open(os.path.join(os.path.dirname(__file__), path)) as fp:
        return fp.read()


def _get_version_match(content):
    # Search for lines of the form: # __version__ = 'ver'
    regex = r"^__version__ = ['\"]([^'\"]*)['\"]"
    version_match = re.search(regex, content, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string in '__init__.py'.")


def get_version():
    try:
        p = Popen(['git', 'describe', '--always', '--tags'],
                  stdout=PIPE, stderr=PIPE)
        p.stderr.close()
        line = p.stdout.readlines()[0]
        describe = line.strip()[1:].decode('utf-8').split('-')
        if len(describe) == 1:
            return describe[0]
        else:
            return describe[0]+'.'+describe[1]

    except Exception as e:
        print(e)
        return _get_version_match(read_file(os.path.join('pysmart-exporter', '__init__.py')))


def get_long_description():
    this_directory = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()

    return long_description


REQUIREMENTS = [
    'prometheus-client',
    'pySMART (>=1.1.0)',
]

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries',
    'Topic :: Software Development :: Libraries :: Python Modules'
]

setup(name='pySMART-exporter',
      version=get_version(),
      description='A Prometheus PySMART exporter',
      url='https://repo1.naudit.es/theseus/pysmart-exporter',
      author='Rafael Leira',
      author_email='rafael.leira@naudit.es',
      license='BSD-3-Clause',
      packages=['pysmart_exporter'],
      install_requires=REQUIREMENTS,
      long_description=get_long_description(),
      long_description_content_type='text/markdown',
      classifiers=CLASSIFIERS,
      entry_points={
          'console_scripts': [
              'pysmart-exporter=pysmart_exporter.__main__:main',
          ]},
      )
