"""Functionality that should be in the standard library. Like
builtins, but Boltons.

Otherwise known as, "everyone's util.py," but cleaned up and
tested.

Contains over 250 BSD-licensed utility types and functions that can be
used as a package or independently. `Extensively documented on Read
the Docs <http://boltons.readthedocs.org>`_.
"""

from setuptools import setup


__author__ = 'Mahmoud Hashemi'
__version__ = '23.1.2dev'
__contact__ = 'mahmoud@hatnote.com'
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
      python_requires='>=3.7',
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
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
          'Programming Language :: Python :: 3.12',
          'Programming Language :: Python :: 3 :: Only',
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: PyPy', ]
      )

"""
A brief checklist for release:

* tox
* git commit (if applicable)
* Bump setup.py version off of -dev
* git commit -a -m "bump version for x.y.z release"
* rm -rf dist/*
* python setup.py sdist bdist_wheel
* twine upload dist/*
* bump docs/conf.py version
* git commit
* git tag -a x.y.z -m "brief summary"
* write CHANGELOG
* git commit
* bump setup.py version onto n+1 dev
* git commit
* git push

"""
