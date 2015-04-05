``fileutils`` - Filesystem helpers
==================================

.. automodule:: boltons.fileutils

Creating, Finding, and Copying
------------------------------

Python's :mod:`os`, :mod:`os.path`, and :mod:`shutil` modules provide
good coverage of file wrangling fundaments, and these functions help
close a few remaining gaps.

.. autofunction:: boltons.fileutils.mkdir_p

.. autofunction:: boltons.fileutils.iter_find_files

.. autofunction:: boltons.fileutils.copytree


Atomic File Saving
------------------

Ideally, the road to success should never put current progress at
risk. That's why overwriting a file should only happen after the task
at hand has completed. And that's exactly what :func:`atomic_save` and
:class:`AtomicSaver` do.

.. autofunction:: boltons.fileutils.atomic_save

.. autoclass:: boltons.fileutils.AtomicSaver

File Permissions
----------------

Linux, BSD, Mac OS, and other Unix-like operating systems all share a
simple, foundational file permission structure that is commonly
complicit in accidental access denial, as well as file
leakage. :class:`FilePerms` was built to increase clarity and cut down
on permission-related accidents when working with files from Python
code.

.. autoclass:: boltons.fileutils.FilePerms
