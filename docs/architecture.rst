Architecture
============



.. _arch_integration:

Integration
-----------

Utility libraries are often used extensively within a project, and
because they are not often fundamental to the architecture of the
application, simplicity and stability may take precedence over version
recency. In these cases, developers can:

  1. Copy the whole ``boltons`` package into a project.
  2. Copy just the ``utils.py`` file that a project requires.

Boltons take this into account by design.  The ``boltons`` package
depends on no packages, making it easy for inclusion into a
project. Furthermore, virtually all individual modules have been
written to be as self-contained as possible, allowing cherrypicking of
functionality into projects.

Design of a ``bolton``
----------------------

``boltons`` aims to be a living library, an ever-expanding collection
of tested and true utilities. For a ``bolton`` to be a ``bolton``, it
should:

  1. Be pure-Python and as self-contained as possible.
  2. Perform a common task or fulfill a common role.
  3. Demonstrate and mitigate some insufficiency in the standard library.
  4. Strive for the standard set forth by the standard library by
     striking a balance between best practice and "good enough",
     correctness and common sense.
  5. Have approachable documentation with at least one helpful
     :mod:`doctest`, links to relevant standard library functionality, as
     well as any 3rd party packages that provide further capabilities.

Themes of ``boltons``
---------------------

1. From the docs (queueutils, iterutils, tzutils)
2. Standard lib reimpl (fileutils.copytree, namedutils.namedtuple)
3. One-off implementations discovered in other libs utils.py or equivalent (strutils.slugify, bytes2human, relative time)
4. More powerful multi-purpose data structures (OMD, IndexedSet, BList, namedlist, Table)
5. Personal practice (debugutils, gcutils, tbutils)
