``mathutils`` - Mathematical functions
======================================

.. automodule:: boltons.mathutils

.. autoclass:: boltons.mathutils.Bits
   :members:
   :undoc-members:

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
