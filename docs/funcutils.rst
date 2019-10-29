``funcutils`` - ``functools`` fixes
===================================

.. automodule:: boltons.funcutils

.. contents:: Sections
   :depth: 3
   :local:

Decoration
----------

`Decorators`_ are among Python's most elegant and succinct language
features, and boltons adds one special function to make them even more
powerful.

.. _Decorators: https://en.wikipedia.org/wiki/Python_syntax_and_semantics#Decorators

.. autofunction:: wraps

Function construction
---------------------

Functions are so key to programming in Python that there will even
arise times where Python functions must be constructed in
Python. Thankfully, Python is a dynamic enough to make this
possible. Boltons makes it easy.

.. autoclass:: FunctionBuilder
   :members:

Improved ``partial``
--------------------

.. autoclass:: partial
.. autoclass:: InstancePartial
.. autoclass:: CachedInstancePartial

Miscellaneous metaprogramming
-----------------------------

.. autofunction:: copy_function
.. autofunction:: dir_dict
.. autofunction:: mro_items
.. autofunction:: format_invocation
.. autofunction:: format_exp_repr
.. autofunction:: format_nonexp_repr
