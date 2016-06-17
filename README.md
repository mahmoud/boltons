# Boltons

*boltons should be builtins.*

Stable release: |release| |versions| |license| |dependencies| |popularity|

Development: |build| |docs| |coverage| |quality|

.. |release| image:: https://img.shields.io/pypi/v/boltons.svg
    :target: https://pypi.python.org/pypi/boltons
    :alt: Last release
.. |versions| image:: https://img.shields.io/pypi/pyversions/boltons.svg
    :target: https://pypi.python.org/pypi/boltons
    :alt: Python versions
.. |license| image:: https://img.shields.io/pypi/l/boltons.svg
    :target: https://www.gnu.org/licenses/gpl-2.0.html
    :alt: Software license
.. |popularity| image:: https://img.shields.io/pypi/dm/boltons.svg
    :target: https://pypi.python.org/pypi/boltons#downloads
    :alt: Popularity
.. |dependencies| image:: https://img.shields.io/requires/github/mahmoud/boltons/master.svg
    :target: https://requires.io/github/mahmoud/boltons/requirements/?branch=master
    :alt: Requirements freshness
.. |build| image:: https://img.shields.io/travis/mahmoud/boltons/develop.svg
    :target: https://travis-ci.org/mahmoud/boltons
    :alt: Unit-tests status
.. |docs| image:: https://readthedocs.org/projects/boltons/badge/?version=latest
    :target: https://boltons.readthedocs.io/en/latest/
    :alt: Documentation Status
.. |coverage| image:: https://codecov.io/github/mahmoud/boltons/coverage.svg?branch=develop
    :target: https://codecov.io/github/mahmoud/boltons?branch=develop
    :alt: Coverage Status
.. |quality| image:: https://img.shields.io/scrutinizer/g/mahmoud/boltons.svg
    :target: https://scrutinizer-ci.com/g/mahmoud/boltons/?branch=develop
    :alt: Code Quality

**Boltons** is a set of over 160 BSD-licensed, pure-Python utilities
in the same spirit as — and yet conspicuously missing from —
[the standard library][stdlib], including:

  * [Atomic file saving][atomic], bolted on with [fileutils][fileutils]
  * A highly-optimized [OrderedMultiDict][omd], in [dictutils][dictutils]
  * *Two* types of [PriorityQueue][pq], in [queueutils][queueutils]
  * [Chunked][chunked] and [windowed][windowed] iteration, in [iterutils][iterutils]
  * Recursive data structure [iteration and merging][remap], with [iterutils.remap][iterutils.remap]
  * Exponential backoff functionality, including jitter, through [iterutils.backoff][iterutils.backoff]
  * A full-featured [TracebackInfo][tbinfo] type, for representing stack traces,
    in [tbutils][tbutils]

**[Full and extensive docs are available on Read The Docs.][rtd]** See
what's new [by checking the CHANGELOG][changelog].

Boltons is tested against Python 2.6, 2.7, 3.4, 3.5, and PyPy.

[stdlib]: https://docs.python.org/2.7/library/index.html
[rtd]: https://boltons.readthedocs.org/en/latest/
[changelog]: https://github.com/mahmoud/boltons/blob/master/CHANGELOG.md

[atomic]: https://boltons.readthedocs.org/en/latest/fileutils.html#boltons.fileutils.atomic_save
[omd]: https://boltons.readthedocs.org/en/latest/dictutils.html#boltons.dictutils.OrderedMultiDict
[pq]: https://boltons.readthedocs.org/en/latest/queueutils.html#boltons.queueutils.PriorityQueue
[chunked]: https://boltons.readthedocs.org/en/latest/iterutils.html#boltons.iterutils.chunked
[windowed]: https://boltons.readthedocs.org/en/latest/iterutils.html#boltons.iterutils.windowed
[tbinfo]: https://boltons.readthedocs.org/en/latest/tbutils.html#boltons.tbutils.TracebackInfo

[fileutils]: https://boltons.readthedocs.org/en/latest/fileutils.html#module-boltons.fileutils
[dictutils]: https://boltons.readthedocs.org/en/latest/dictutils.html#module-boltons.dictutils
[queueutils]: https://boltons.readthedocs.org/en/latest/queueutils.html#module-boltons.queueutils
[iterutils]: https://boltons.readthedocs.org/en/latest/iterutils.html#module-boltons.iterutils
[iterutils.remap]: http://boltons.readthedocs.org/en/latest/iterutils.html#boltons.iterutils.remap
[iterutils.backoff]: http://boltons.readthedocs.org/en/latest/iterutils.html#boltons.iterutils.backoff
[tbutils]: https://boltons.readthedocs.org/en/latest/tbutils.html#module-boltons.tbutils

[remap]: http://sedimental.org/remap.html

## Installation

Boltons can be added to a project in a few ways. There's the obvious one:

```
    pip install boltons
```

Then, [thanks to PyPI][boltons_pypi], dozens of boltons are just an import away:

```python
    from boltons.cacheutils import LRU
    my_cache = LRU()
```

However, due to the nature of utilities, application developers might
want to consider other options, including vendorization of individual
modules into a project. Boltons is pure-Python and has no
dependencies. If the whole project is too big, each module is
independent, and can be copied directly into a project. See the
[Integration][integration] section of the docs for more details.

[boltons_pypi]: https://pypi.python.org/pypi/boltons
[integration]: https://boltons.readthedocs.org/en/latest/architecture.html#integration

## Third-party packages

The majority of boltons strive to be "good enough" for a wide range of
basic uses, leaving advanced use cases to Python's [myriad specialized
3rd-party libraries][pypi]. In many cases the respective ``boltons`` module
will describe 3rd-party alternatives worth investigating when use
cases outgrow `boltons`. If you've found a natural "next-step"
library worth mentioning, see the next section!

[pypi]: https://pypi.python.org/pypi

## Gaps

Found something missing in the standard library that should be in
`boltons`? Found something missing in `boltons`? First, take a
moment to read the very brief [architecture statement][architecture] to make
sure the functionality would be a good fit.

Then, if you are very motivated, submit [a Pull Request][prs]. Otherwise,
submit a short feature request on [the Issues page][issues], and we will
figure something out.

[architecture]: https://boltons.readthedocs.org/en/latest/architecture.html
[issues]: https://github.com/mahmoud/boltons/issues
[prs]: https://github.com/mahmoud/boltons/pulls
