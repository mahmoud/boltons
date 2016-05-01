``socketutils`` - ``socket`` wrappers
=====================================

.. automodule:: boltons.socketutils

BufferedSocket
--------------

.. autoclass:: boltons.socketutils.BufferedSocket
   :members:

Exceptions
^^^^^^^^^^

These are a few exceptions that derive from :exc:`socket.error` and
provide clearer code and better error messages.

.. autoexception:: boltons.socketutils.Error
.. autoexception:: boltons.socketutils.Timeout
.. autoexception:: boltons.socketutils.ConnectionClosed
.. autoexception:: boltons.socketutils.MessageTooLong

Netstring
---------

.. autoclass:: boltons.socketutils.NetstringSocket
   :members:

Nestring Exceptions
^^^^^^^^^^^^^^^^^^^

These are a few higher-level exceptions for Netstring connections.

.. autoexception:: boltons.socketutils.NetstringProtocolError
.. autoexception:: boltons.socketutils.NetstringInvalidSize
.. autoexception:: boltons.socketutils.NetstringMessageTooLong
