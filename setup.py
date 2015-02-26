"""
    Functionality that should be in the standard library. Like
    builtins. But Boltons.

    Otherwise known as "everyone's util.py," but cleaned up and
    tested.

    :copyright: (c) 2015 by Mahmoud Hashemi
    :license: BSD, see LICENSE for more details.
"""

import sys
from setuptools import setup


__author__ = 'Mahmoud Hashemi'
__version__ = '0.4.2dev'
__contact__ = 'mahmoudrhashemi@gmail.com'
__url__ = 'https://github.com/mahmoud/boltons'
__license__ = 'BSD'


if sys.version_info >= (3,):
    raise NotImplementedError("boltons Python 3 support en route to your location")


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
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Libraries',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7', ]
      )
