.. boltons documentation master file, created on Sat Mar 21 00:34:18 2015.
boltons
=======

*boltons should be builtins.*

**Boltons** is a set of pure-Python utilities in the same spirit as —
and yet conspicuously missing from — the `the standard library`_,
including:

  * :func:`Atomic file saving <boltons.fileutils.atomic_save>`, bolted on with
    :mod:`~boltons.fileutils`
  * A highly-optimized :class:`~boltons.dictutils.OrderedMultiDict`,
    in :mod:`boltons.dictutils`
  * Two types of :class:`~boltons.queueutils.PriorityQueue`, in
    :mod:`boltons.queueutils`
  * :func:`Chunked <boltons.iterutils.chunked>` and :func:`windowed
    <boltons.iterutils.windowed>` iteration, in :mod:`boltons.iterutils`
  * A full-featured :class:`~boltons.tbutils.TracebackInfo` type, for
    representing stack traces, in :mod:`boltons.tbutils`

And that's just a small selection. As of |today|, ``boltons`` is
|b_type_count| types and |b_func_count| functions spread across
|b_mod_count| modules.

.. counts are appx 50, 75, and 23, respectively, as of initial docs writing

.. _the standard library: https://docs.python.org/2.7/library/index.html

Installation and Integration
----------------------------

Boltons can be added to a project in a few ways. There's the obvious one::

  pip install boltons

Then dozens of boltons are just an import away::

  from boltons.cacheutils import LRU
  my_cache = LRU()

However, because of the nature of utilities, application developers
might want to consider other options. See the
:ref:`Integration <arch_integration>` section for more details.

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
   fileutils
   formatutils
   funcutils
   gcutils
   iterutils
   jsonutils
   listutils
   mboxutils
   namedutils
   queueutils
   setutils
   statsutils
   strutils
   tableutils
   tbutils
   timeutils
   tzutils
