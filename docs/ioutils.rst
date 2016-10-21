``ioutils`` - Input/Output Utilities
====================================

.. automodule:: boltons.ioutils

Spooled Temporary Files
-----------------------
Spooled Temporary Files are file-like objects that start out mapped to
in-memory objects, but automatically roll over to a temporary file once they
reach a certain (configurable) threshhold. Unfortunately the built-in
SpooledTemporaryFile class in Python does not implement the exact API that some
common classes like StringIO do. SpooledTemporaryFile also spools all of it's
in-memory files as cStringIO instances. cStringIO instances cannot be
deep-copied, and they don't work with the zip library either. This along with
the incompatible api makes it useless for several use-cases.

To combat this but still gain the memory savings and usefulness of a true
spooled file-like-object, two custom classes have been implemented which have
a compatible API.

.. _spooledbytesio:

SpooledBytesIO
^^^^^^^^^^^^^^
.. autoclass:: boltons.ioutils.SpooledBytesIO

SpooledStringIO
^^^^^^^^^^^^^^^
.. autoclass:: boltons.ioutils.SpooledStringIO
