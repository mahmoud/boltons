``urlutils`` - Structured URL
=============================

.. automodule:: boltons.urlutils

.. versionadded:: 17.2

The ``URL``
-----------

.. autoclass:: boltons.urlutils.URL
   :members:

Related functions
~~~~~~~~~~~~~~~~~

.. autofunction:: boltons.urlutils.find_all_links

.. autofunction:: boltons.urlutils.register_scheme


Low-level functions
-------------------

A slew of functions used internally by :class:`~boltons.urlutils.URL`.

.. autofunction:: boltons.urlutils.parse_url
.. autofunction:: boltons.urlutils.parse_host
.. autofunction:: boltons.urlutils.parse_qsl
.. autofunction:: boltons.urlutils.resolve_path_parts

.. autoclass:: boltons.urlutils.QueryParamDict
   :members:

Quoting
~~~~~~~

URLs have many parts, and almost as many individual "quoting"
(encoding) strategies.

.. autofunction:: boltons.urlutils.quote_userinfo_part
.. autofunction:: boltons.urlutils.quote_path_part
.. autofunction:: boltons.urlutils.quote_query_part
.. autofunction:: boltons.urlutils.quote_fragment_part

There is however, only one unquoting strategy:

.. autofunction:: boltons.urlutils.unquote
