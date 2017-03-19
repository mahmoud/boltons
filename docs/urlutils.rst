``urlutils`` - Structured URL
=============================

.. automodule:: boltons.urlutils

.. versionadded:: 17.2

The URL type
------------

.. autoclass:: boltons.urlutils.URL

   .. attribute:: URL.scheme

      The scheme is an ASCII string, normally lowercase, which
      specifies the semantics for the rest of the URL, as well as
      network protocol in many cases. For example, "http" in
      "http://hatnote.com".

   .. attribute:: URL.username

      The username is a string used by some schemes for
      authentication. For example, "public" in
      "ftp://public@example.com".

   .. attribute:: URL.password

      The password is a string also used for
      authentication. Technically deprecated by `RFC 3986 Section
      7.5`_, they're still used in cases when the URL is private or
      the password is public. For example "password" in
      "db://private:password@127.0.0.1".

      .. _RFC 3986 Section 7.5: https://tools.ietf.org/html/rfc3986#section-7.5

   .. attribute:: URL.host

      The host is a string used to resolve the network location of the
      resource, either empty, a domain, or IP address (v4 or
      v6). "example.com", "127.0.0.1", and "::1" are all good examples
      of host strings.

      Per spec, fully-encoded output from :attr:`~URL.to_text()` is
      `IDNA encoded`_ for compatibility with DNS.

      .. _IDNA encoded: https://en.wikipedia.org/wiki/Internationalized_domain_name#Example_of_IDNA_encoding

   .. attribute:: URL.port

      The port is an integer used, along with :attr:`host`, in
      connecting to network locations. ``8080`` is the port in
      "http://localhost:8080/index.html".

      .. note::

         As is the case for 80 for HTTP and 22 for SSH, many schemes
         have default ports, and `Section 3.2.3 of RFC 3986`_ states
         that when a URL's port is the same as its scheme's default
         port, the port should not be emitted::

           >>> URL(u'https://github.com:443/mahmoud/boltons').to_text()
           u'https://github.com/mahmoud/boltons'

         Custom schemes can register their port with
         :func:`~boltons.urlutils.register_scheme`. See
         :attr:`URL.default_port` for more info.

         .. _Section 3.2.3 of RFC 3986: https://tools.ietf.org/html/rfc3986#section-3.2.3

   .. attribute:: URL.path

      The string starting with the first leading slash after the
      authority part of the URL, ending with the first question
      mark. Often percent-quoted for network use. "/a/b/c" is the path
      of "http://example.com/a/b/c?d=e".


   .. attribute:: URL.path_parts

      The :class:`tuple` form of :attr:`~URL.path`, split on
      slashes. Empty slash segments are preserved, including that of
      the leading slash::

        >>> url = URL(u'http://example.com/a/b/c')
        >>> url.path_parts
        (u'', u'a', u'b', u'c')


   .. attribute:: URL.query_params

      An instance of :class:`~boltons.urlutils.QueryParamDict`, an
      :class:`~boltons.dictutils.OrderedMultiDict` subtype, mapping
      textual keys and values which follow the first question mark
      after the :attr:`path`. Also available as the handy alias
      ``qp``::

        >>> url = URL('http://boltons.readthedocs.io/en/latest/?utm_source=docs&sphinx=ok')
        >>> url.qp.keys()
        [u'utm_source', u'sphinx']

      Also percent-encoded for network use cases.

   .. attribute:: URL.fragment

      The string following the first '#' after the
      :attr:`query_params` until the end of the URL. It has no
      inherent internal structure, and is percent-quoted.

   .. automethod:: URL.from_parts
   .. automethod:: URL.to_text

   .. autoattribute:: URL.default_port
   .. autoattribute:: URL.uses_netloc

   .. automethod:: URL.get_authority

   .. automethod:: URL.normalize
   .. automethod:: URL.navigate



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

Useful constants
----------------

.. attribute:: boltons.urlutils.SCHEME_PORT_MAP

   A mapping of URL schemes to their protocols' default
   ports. Painstakingly assembled from the `IANA scheme registry`_,
   `port registry`_, and independent research.

   Keys are lowercase strings, values are integers or None, with None
   indicating that the scheme does not have a default port (or may not
   support ports at all)::

     >>> boltons.urlutils.SCHEME_PORT_MAP['http']
     80
     >>> boltons.urlutils.SCHEME_PORT_MAP['file']
     None

   See :attr:`URL.port` for more info on how it is used. See
   :attr:`~boltons.urlutils.NO_NETLOC_SCHEMES` for more scheme info.

   Also `available in JSON`_.

   .. _IANA scheme registry: https://www.iana.org/assignments/uri-schemes/uri-schemes.xhtml
   .. _port registry: https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml
   .. _available in JSON: https://gist.github.com/mahmoud/2fe281a8daaff26cfe9c15d2c5bf5c8b


.. attribute:: boltons.urlutils.NO_NETLOC_SCHEMES

   This is a :class:`set` of schemes explicitly do not support network
   resolution, such as "mailto" and "urn".
