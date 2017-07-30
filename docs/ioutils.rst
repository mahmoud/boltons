``ioutils`` - Input/output enhancements
=======================================

.. automodule:: boltons.ioutils

Spooled Temporary Files
-----------------------
Spooled Temporary Files are file-like objects that start out mapped to
in-memory objects, but automatically roll over to a temporary file once they
reach a certain (configurable) threshold. Unfortunately the built-in
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

.. _spooledstringio:

SpooledStringIO
^^^^^^^^^^^^^^^
.. autoclass:: boltons.ioutils.SpooledStringIO


Examples
--------
It's not uncommon to find excessive usage of StringIO in older Python code. A
SpooledTemporaryFile would be a nice replacement if one wanted to reduce memory
overhead, but unfortunately its api differs too much. This is a good candidate
for :ref:`spooledbytesio` as it is api compatible and thus may be used as a
drop-in replacement.

Old Code::

    flo = StringIO()
    flo.write(gigantic_string)

Updated::

    from boltons.ioutils import SpooledBytesIO

    flo = SpooledBytesIO()
    flo.write(gigantic_string)


Another good use case is downloading a file from some remote location. It's
nice to keep it in memory if it's small, but writing a large file into memory
can make servers quite grumpy. If the file being downloaded happens to be a zip
file then things are worse. You can't use a normal SpooledTemporaryFile because
it isn't compatible. A :ref:`spooledbytesio` instance is a good alternative.
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
