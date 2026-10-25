``ioutils`` - Input/output enhancements
=======================================

.. automodule:: boltons.ioutils

Spooled Temporary Files
-----------------------
Spooled Temporary Files are file-like objects that start out mapped to
in-memory objects, but automatically roll over to a temporary file once they
reach a certain (configurable) threshold. Boltons provides two of them, with
the same API as their :mod:`io` counterparts: :ref:`spooledbytesio` for binary
data, like :class:`io.BytesIO`, and :ref:`spooledstringio` for text, like
:class:`io.StringIO`. ``SpooledBytesIO.write()`` takes bytes;
``SpooledStringIO.write()`` takes strings.

.. _spooledbytesio:

SpooledBytesIO
^^^^^^^^^^^^^^
.. autoclass:: boltons.ioutils.SpooledBytesIO

.. _spooledstringio:

SpooledStringIO
^^^^^^^^^^^^^^^
.. autoclass:: boltons.ioutils.SpooledStringIO


Examples
--------
When text held in an :class:`io.StringIO` may grow large,
:ref:`spooledstringio` is a drop-in replacement that reduces memory overhead
by rolling over to a temporary file.

Old Code::

    from io import StringIO

    gigantic_string = 'example text ' * 100000
    flo = StringIO()
    flo.write(gigantic_string)

Updated::

    from boltons.ioutils import SpooledStringIO

    gigantic_string = 'example text ' * 100000
    flo = SpooledStringIO()
    flo.write(gigantic_string)


Another good use case is downloading a file from some remote location. It's
nice to keep it in memory if it's small, but writing a large file into memory
can make servers quite grumpy. If the file being downloaded happens to be a zip
file, the stream must hold bytes and support seeking. A :ref:`spooledbytesio`
instance works well here, as does a binary :class:`tempfile.SpooledTemporaryFile`.
Here is a simple example using the requests library to download a zip file::

    from zipfile import ZipFile

    import requests
    from boltons import ioutils

    # Using a context manager with stream=True ensures the connection is closed. See:
    # http://docs.python-requests.org/en/master/user/advanced/#body-content-workflow
    with requests.get("http://127.0.0.1/test_file.zip", stream=True) as r:
        if r.status_code == 200:
            with ioutils.SpooledBytesIO() as flo:
                for chunk in r.iter_content(chunk_size=64000):
                    flo.write(chunk)

                flo.seek(0)

                zip_doc = ZipFile(flo)

                # Print all the files in the zip
                print(zip_doc.namelist())


Multiple Files
--------------

.. _multifilereader:

MultiFileReader
^^^^^^^^^^^^^^^
.. autoclass:: boltons.ioutils.MultiFileReader
