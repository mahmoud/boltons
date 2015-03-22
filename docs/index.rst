.. boltons documentation master file, created on Sat Mar 21 00:34:18 2015.


boltons
=======

*boltons should be builtins.*

**Boltons** is a set of pure-Python utilities in the same spirit as
the Python builtins, and yet somehow not present in the standard
library. A few examples include:

* Atomic file saving, bolted on with fileutils
* A highly-optimized ``OrderedMultiDict``, in dictutils
* Two types of ``PriorityQueue``, in queueutils
* "Chunked" and "windowed" iteration, among many others, in iterutils
* A full-featured ``TracebackInfo`` type, for representing stack traces, in tbutils

Usage
-----

Boltons can be used in a couple ways.

  1. Install the boltons package using ``pip`` or ``easy_install``.
  2. Copy the whole boltons package into your project.
  2. Copy just the ``utils.py`` module that your package needs.

The boltons package depends on no packages, making it easy for
inclusion into a project. Furthermore, most individual modules have
been written to be as self-contained as possible, allowing
cherrypicking of functionality into projects. Basically, there are no
hard-and-fast rules when it comes to utils.


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

Contents:

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
   osutils
   queueutils
   setutils
   statsutils
   strutils
   tableutils
   tbutils
   timeutils
   tzutils
