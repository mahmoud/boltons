.. boltons documentation master file, created on Sat Mar 21 00:34:18 2015.
boltons
=======

*boltons should be builtins.*

**Boltons** is a set of pure-Python utilities in the same spirit as
the Python builtins, and yet conspicuously missing from the `the
standard library`_. A few examples include:

  * Atomic file saving, bolted on with :mod:`fileutils`
  * A highly-optimized :class:`OrderedMultiDict`, in :mod:`dictutils`
  * Two types of ``PriorityQueue``, in :mod:`queueutils`
  * "Chunked" and "windowed" iteration, among many others, in :mod:`iterutils`
  * A full-featured ``TracebackInfo`` type, for representing stack
    traces, in :mod:`tbutils`

.. _the standard library: https://docs.python.org/2.7/library/index.html

Installation and Integration
----------------------------

Boltons can be added to a project in a few ways. There's the obvious one::

  pip install boltons

Then just import away::

  from boltons.cacheutils import LRU
  my_cache = LRU()

However, because of the nature of utilities, application developers
might want to consider other options. See the
:ref:`Integration <arch_integration>` section for more details.

Third-party packages
--------------------

The majority of boltons strive to be "good enough" for a wide range of
basic uses, leaving advanced use cases to specialized 3rd party
libraries. For example, no radical recommendations of NumPy inclusion
in the standard lib; the builtin number types and operations are
great! Built-in support for imaginary numbers for goodness sake!

Gaps
----

.. appx 50, 75, and 20, respectively

Boltons is |b_type_count| types and |b_func_count| functions spread
across |b_mod_count| modules. Gaps are bound to be found.

Found something missing in the standard library that should be in
``boltons``? First, take a moment to read the very brief
:doc:`architecture` statement to make sure the functionality would be
a good fit.

Then, if you are very motivated, submit `a Pull
Request`_. Otherwise, submit a feature request on `the Issues page`_,
and we will figure something out.

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
