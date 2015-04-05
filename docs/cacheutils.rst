``cacheutils`` - Caches and caching
===================================

.. automodule:: boltons.cacheutils


Least-Recently Inserted (LRI)
-----------------------------

The :class:`LRI` is the simpler cache, implementing a very simple first-in,
first-out (FIFO) approach to cache eviction. If the use case calls for
simple, very-low overhead caching, such as somewhat expensive local
operations (e.g., string operations), then the LRI is likely the right
choice.

.. autoclass:: boltons.cacheutils.LRI
   :members:

Least-Recently Used (LRU)
-------------------------

The :class:`LRU` is the more advanced cache, but it's still quite
simple. When it reaches capacity, it replaces the least-recently used
item. This strategy makes the LRU a more effective cache than the LRI
for a wide variety of applications, but also entails more operations
for all of its APIs, especially reads. Unlike the :class:`LRI`, the
LRU has threadsafety built in.

.. autoclass:: boltons.cacheutils.LRU
   :members:


Automatic function caching
--------------------------

Continuing in the theme of cache tunability and experimentation,
``cacheutils`` also offers a way to pluggably cache function return
values: the :func:`cached` function decorator.

.. autofunction:: boltons.cacheutils.cached

Similar functionality can be found in Python 3.4's :mod:`functools`
module, though it is made for cache pluggability and does not support
sharing the cache object across multiple functions.
