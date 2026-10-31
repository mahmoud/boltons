``mathutils`` - Mathematical functions
======================================

.. automodule:: boltons.mathutils

.. autoclass:: boltons.mathutils.Bits
   :members:
   :undoc-members:

Range Operations
----------------

These helpers operate on closed ranges of comparable endpoints, including
numbers, strings, and dates. They accept unsorted iterables without modifying
them. Touching ranges share their endpoint. Reversed bounds and NaN endpoints
raise :exc:`ValueError`.

.. autofunction:: boltons.mathutils.range_union

.. autofunction:: boltons.mathutils.range_intersection

Alternative Rounding Functions
------------------------------

.. autofunction:: boltons.mathutils.clamp

.. autofunction:: boltons.mathutils.ceil

.. autofunction:: boltons.mathutils.floor

Note: :func:`ceil` and :func:`floor` functions are based on `this example`_ using from the
:mod:`bisect` module in the standard library. Refer to this `StackOverflow Answer`_ for further information regarding
the performance impact of this approach.

.. _this example: https://docs.python.org/3/library/bisect.html#searching-sorted-lists
.. _StackOverflow Answer: http://stackoverflow.com/a/12141511/811740
