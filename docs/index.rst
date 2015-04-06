.. boltons documentation master file, created on Sat Mar 21 00:34:18 2015.
boltons
=======

*boltons should be builtins.*

**Boltons** is a set of pure-Python utilities in the same spirit as
the Python builtins, and yet somehow not present in `the standard
library`_. A few examples include:

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
might want to consider:

  1. Copying the whole ``boltons`` package into your project.
  2. Copying just the ``utils.py`` file that your package requires.

Utility libraries are often used extensively within a project, and
because they are not often fundamental to the architecture of the
application, simplicity and stability may take precedence over version
recency. Boltons take this into account by design.

Design of a ``bolton``
----------------------

``boltons`` aims to be a living library, an ever-expanding collection
of tested and true utilities. For a ``bolton`` to be a ``bolton``, it
should:

  1. Be pure-Python and as self-contained as possible.
  2. Perform a common task or fulfill a common role.
  3. Demonstrate and mitigate some insufficiency in the standard library.
  4. Strive for the standard set forth by the standard library by
     striking a balance between best practice and "good enough",
     correctness and common sense.

The ``boltons`` package depends on no packages, making it easy for
inclusion into a project. Furthermore, virtually all individual modules have
been written to be as self-contained as possible, allowing
cherrypicking of functionality into projects.

Themes of ``boltons``
---------------------

1. From the docs (queueutils, iterutils, tzutils)
2. Standard lib reimpl (fileutils.copytree, namedutils.namedtuple)
3. One-off implementations discovered in other libs utils.py or equivalent (strutils.slugify, bytes2human, relative time)
4. More powerful multi-purpose data structures (OMD, IndexedSet, BList, namedlist, Table)
5. Personal practice (debugutils, gcutils, tbutils)

Third-party packages
--------------------

The majority of boltons strive to be "good enough" for a wide range of
basic uses, leaving advanced use cases to specialized 3rd party
libraries. For example, no radical recommendations of NumPy inclusion
in the standard lib; the builtin number types and operations are
great! Built-in support for imaginary numbers for goodness sake!

Gaps
----

Found something missing in boltons? If you are very motivated, submit
a Pull Request. Otherwise, submit a feature request on the Issues
page, and we will figure something out.

Section listing
---------------

.. toctree::
   :maxdepth: 2

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
