.. boltons documentation master file, created on Sat Mar 21 00:34:18 2015.
boltons
=======

*boltons should be builtins.*

|release| |calver| |changelog|

**Boltons** is a set of pure-Python utilities in the same spirit as —
and yet conspicuously missing from — `the standard library`_,
including:

  * :func:`Atomic file saving <boltons.fileutils.atomic_save>`, bolted on with
    :mod:`~boltons.fileutils`
  * A highly-optimized :class:`~boltons.dictutils.OrderedMultiDict`,
    in :mod:`~boltons.dictutils`
  * Two types of :class:`~boltons.queueutils.PriorityQueue`, in
    :mod:`~boltons.queueutils`
  * :func:`Chunked <boltons.iterutils.chunked>` and
    :func:`windowed <boltons.iterutils.windowed>` iteration, in
    :mod:`~boltons.iterutils`
  * A full-featured :class:`~boltons.tbutils.TracebackInfo` type, for
    representing stack traces, in :mod:`~boltons.tbutils`
  * A lightweight :class:`UTC timezone <boltons.timeutils.UTC>`
    available in :mod:`~boltons.timeutils`.
  * Recursive mapping for nested data transforms, with :func:`remap
    <boltons.iterutils.remap>`

And that's just a small selection. As of |today|, ``boltons`` is
|b_type_count| types and |b_func_count| functions, spread across
|b_mod_count| modules. See them all in the :ref:`genindex`, and see
what's new by `checking the CHANGELOG`_.

.. counts are appx 50, 75, and 23, respectively, as of initial docs writing
.. in mid 2016, the counts are now 62, 112, and 25, respectively

.. _the standard library: https://docs.python.org/3/library/index.html
.. _checking the CHANGELOG: https://github.com/mahmoud/boltons/blob/master/CHANGELOG.md

.. |release| image:: https://img.shields.io/pypi/v/boltons.svg
             :target: https://pypi.python.org/pypi/boltons

.. |calver| image:: https://img.shields.io/badge/calver-YY.MINOR.MICRO-22bfda.svg
            :target: http://calver.org

.. |changelog| image:: https://img.shields.io/badge/CHANGELOG-UPDATED-b84ad6.svg
               :target: https://github.com/mahmoud/boltons/blob/master/CHANGELOG.md

Installation and Integration
----------------------------

Boltons can be added to a project in a few ways. There's the obvious one::

  pip install boltons

On macOS, it can also be installed via `MacPorts`_::

  sudo port install py-boltons

Then dozens of boltons are just an import away::

  from boltons.cacheutils import LRU
  lru_cache = LRU()
  lru_cache['result'] = 'success'

Due to the nature of utilities, application developers might want to
consider other integration options. See the :ref:`Integration
<arch_integration>` section of the architecture document for more
details.

Boltons is tested against Python 3.7-3.13, as well as PyPy3.

.. _MacPorts: https://ports.macports.org/port/py-boltons/summary

Third-party packages
--------------------

The majority of boltons strive to be "good enough" for a wide range of
basic uses, leaving advanced use cases to Python's `myriad specialized
3rd-party libraries`_. In many cases the respective ``boltons`` module
will describe 3rd-party alternatives worth investigating when use
cases outgrow ``boltons``. If you've found a natural "next-step"
library worth mentioning, :ref:`consider filing an issue <Gaps>`!

.. _myriad specialized 3rd-party libraries: https://pypi.python.org/pypi

.. _gaps:

Gaps
----

Found something missing in the standard library that should be in
``boltons``? Found something missing in ``boltons``? First, take a
moment to read the very brief :doc:`architecture` statement to make
sure the functionality would be a good fit.

Then, if you are very motivated, submit `a Pull Request`_. Otherwise,
submit a short feature request on `the Issues page`_, and we will
figure something out.

.. _a Pull Request: https://github.com/mahmoud/boltons/pulls
.. _the Issues Page: https://github.com/mahmoud/boltons/issues

Section listing
---------------

.. toctree::
   :maxdepth: 2

   architecture
   cacheutils
   debugutils
   dictutils
   ecoutils
   fileutils
   formatutils
   funcutils
   gcutils
   ioutils
   iterutils
   jsonutils
   listutils
   mathutils
   mboxutils
   namedutils
   pathutils
   queueutils
   setutils
   socketutils
   statsutils
   strutils
   tableutils
   tbutils
   timeutils
   typeutils
   urlutils

(For a quick reference you can ctrl-F, see the :ref:`genindex`.)
