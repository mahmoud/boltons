``fileutils`` - Filesystem helpers
==================================

.. automodule:: boltons.fileutils

Creating, Finding, and Copying
------------------------------

Python's :mod:`os`, :mod:`os.path`, and :mod:`shutil` modules provide
good coverage of file wrangling fundamentals, and these functions help
close a few remaining gaps.

.. autofunction:: boltons.fileutils.mkdir_p

.. autofunction:: boltons.fileutils.iter_find_files

.. autofunction:: boltons.fileutils.copytree

.. autofunction:: boltons.fileutils.rotate_file


Atomic File Saving
------------------

Ideally, the road to success should never put current progress at
risk. And that's exactly why :func:`atomic_save` and
:class:`AtomicSaver` exist.

Using the same API as a writable file, all output is saved to a
temporary file, and when the file is closed, the old file is replaced
by the new file in a single system call, portable across all major
operating systems. No more partially-written or partially-overwritten
files.

.. autofunction:: boltons.fileutils.atomic_save

.. autoclass:: boltons.fileutils.AtomicSaver

.. autofunction:: boltons.fileutils.atomic_rename

.. autofunction:: boltons.fileutils.replace

File Permissions
----------------

Linux, BSD, Mac OS, and other Unix-like operating systems all share a
simple, foundational file permission structure that is commonly
complicit in accidental access denial, as well as file
leakage. :class:`FilePerms` was built to increase clarity and cut down
on permission-related accidents when working with files from Python
code.

.. autoclass:: boltons.fileutils.FilePerms


Miscellaneous
-------------

.. autoclass:: boltons.fileutils.DummyFile
