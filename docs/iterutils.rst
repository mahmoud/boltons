``iterutils`` - ``itertools`` improvements
==========================================

.. automodule:: boltons.iterutils

Iteration
---------

These are generators and convenient :class:`list`-producing
counterparts comprising several common patterns of iteration missing
from the standard library.

.. autofunction:: split
.. autofunction:: split_iter
.. autofunction:: chunked
.. autofunction:: chunked_iter
.. autofunction:: pairwise
.. autofunction:: pairwise_iter
.. autofunction:: windowed
.. autofunction:: windowed_iter
.. autofunction:: backoff
.. autofunction:: backoff_iter
.. autofunction:: unique
.. autofunction:: unique_iter
.. autofunction:: frange
.. autofunction:: xfrange

Categorization
--------------

These functions operate on iterables, dividing into groups based on a given condition.

.. autofunction:: bucketize
.. autofunction:: partition
.. autofunction:: one
.. autofunction:: first


Type Checks
-----------

In the same vein as the feature-checking builtin, :func:`callable`.

.. autofunction:: is_iterable
.. autofunction:: is_scalar
.. autofunction:: is_collection
