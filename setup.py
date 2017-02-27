"""Functionality that should be in the standard library. Like
builtins, but Boltons.

Otherwise known as, "everyone's util.py," but cleaned up and
tested.

Contains over 160 BSD-licensed utility types and functions that can be
used as a package or independently. `Extensively documented on Read
the Docs <http://boltons.readthedocs.org>`_.
"""

from setuptools import setup


__author__ = 'Mahmoud Hashemi'
__version__ = '17.1.1dev'
__contact__ = 'mahmoudrhashemi@gmail.com'
__url__ = 'https://github.com/mahmoud/boltons'
__license__ = 'BSD'


setup(name='boltons',
      version=__version__,
      description="When they're not builtins, they're boltons.",
      long_description=__doc__,
      author=__author__,
      author_email=__contact__,
      url=__url__,
      packages=['boltons'],
      include_package_data=True,
      zip_safe=False,
      license=__license__,
      platforms='any',
      classifiers=[
          # See: https://pypi.python.org/pypi?:action=list_classifiers
          'Topic :: Utilities',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Topic :: Software Development :: Libraries',
          'Development Status :: 5 - Production/Stable',
          'Operating System :: OS Independent',
          # List of python versions and their support status:
          # https://en.wikipedia.org/wiki/CPython#Version_history
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: PyPy', ]
      )

"""
A brief checklist for release:

* tox
* git commit (if applicable)
* Bump setup.py version off of -dev
* git commit -a -m "bump version for x.y.z release"
* python setup.py sdist bdist_wheel upload
* bump docs/conf.py version
* git commit
* git tag -a x.y.z -m "brief summary"
* write CHANGELOG
* git commit
* bump setup.py version onto n+1 dev
* git commit
* git push

"""
