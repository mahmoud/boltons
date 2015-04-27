``mathutils`` - General purpose math functions
==============================================

.. automodule:: boltons.mathutils

Alternative Ceiling/Floor Functions
-----------------------------------

.. autofunction:: boltons.mathutils.ceil_from_iter

.. autofunction:: boltons.mathutils.floor_from_iter

Note: :func:`ceil_from_iter` and :func:`floor_from_iter` functions are based on `this example`_ using from the
:mod:`bisect` module in the standard library. Refer to this `StackOverflow Answer`_ for further information regarding
the performance impact of this approach.

.. _this example: https://docs.python.org/3/library/bisect.html#searching-sorted-lists
.. _StackOverflow Answer: http://stackoverflow.com/a/12141511/811740