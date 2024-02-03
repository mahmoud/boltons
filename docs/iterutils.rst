``iterutils`` - ``itertools`` improvements
==========================================

.. automodule:: boltons.iterutils

.. contents:: Sections
   :depth: 3
   :local:

.. _iteration:

Iteration
---------

These are generators and convenient :class:`list`-producing
counterparts comprising several common patterns of iteration not
present in the standard library.

.. autofunction:: chunked
.. autofunction:: chunked_iter
.. autofunction:: chunk_ranges
.. autofunction:: pairwise
.. autofunction:: pairwise_iter
.. autofunction:: windowed
.. autofunction:: windowed_iter
.. autofunction:: unique
.. autofunction:: unique_iter
.. autofunction:: redundant

Stripping and splitting
-----------------------

A couple of :class:`str`-inspired mechanics that have come in handy on
iterables, too:

.. autofunction:: split
.. autofunction:: split_iter
.. autofunction:: strip
.. autofunction:: strip_iter
.. autofunction:: lstrip
.. autofunction:: lstrip_iter
.. autofunction:: rstrip
.. autofunction:: rstrip_iter

Nested
------

Nested data structures are common. Yet virtually all of Python's
compact iteration tools work with flat data: list comprehensions,
map/filter, generator expressions, itertools, even other
iterutils.

The functions below make working with nested iterables and other
containers as succinct and powerful as Python itself.

.. autofunction:: remap
.. autofunction:: get_path
.. autofunction:: research
.. autofunction:: flatten
.. autofunction:: flatten_iter

Numeric
-------

Number sequences are an obvious target of Python iteration, such as
the built-in :func:`range`, and
:func:`itertools.count`. Like the :ref:`iteration` members above,
these return iterators and lists, but take numeric inputs instead of
iterables.

.. autofunction:: backoff
.. autofunction:: backoff_iter
.. autofunction:: frange
.. autofunction:: xfrange


Categorization
--------------

These functions operate on iterables, dividing into groups based on a
given condition.

.. autofunction:: bucketize
.. autofunction:: partition

Sorting
-------

The built-in :func:`sorted()` is great, but what do you do when you want to
partially override the sort order?

.. autofunction:: soft_sorted
.. autofunction:: untyped_sorted

Reduction
---------

:func:`reduce` is a powerful function, but it is also very open-ended
and not always the most readable. The standard library recognized this
with the addition of :func:`sum`, :func:`all`, and :func:`any`. All
these functions take a basic operator (``+``, ``and``, and ``or``) and
use the operator to turn an iterable into a single value.

Functions in this category follow that same spirit, turning iterables
like lists into single values:

.. autofunction:: one
.. autofunction:: first
.. autofunction:: same

Type Checks
-----------

In the same vein as the feature-checking builtin, :func:`callable`.

.. autofunction:: is_iterable
.. autofunction:: is_scalar
.. autofunction:: is_collection
