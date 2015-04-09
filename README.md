# Boltons

*boltons should be builtins.*

**Boltons** is a set of over 100 BSD-licensed, pure-Python utilities
in the same spirit as — and yet conspicuously missing from — the
[the standard library][stdlib], including:

  * [Atomic file saving][atomic], bolted on with [fileutils][fileutils]
  * A highly-optimized [OrderedMultiDict][omd], in [dictutils][dictutils]
  * *Two* types of [PriorityQueue][pq], in [queueutils][queueutils]
  * [Chunked][chunked] and [windowed][windowed] iteration, in [iterutils][iterutils]
  * A full-featured [TracebackInfo][tbinfo] type, for representing stack traces,
    in [tbutils][tbutils]

[Full and extensive docs are available on Read The Docs.][rtd]

[stdlib]: https://docs.python.org/2.7/library/index.html
[rtd]: https://boltons.readthedocs.org/en/latest/

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
[tbutils]: https://boltons.readthedocs.org/en/latest/tbutils.html#module-boltons.tbutils

## Installation

Boltons can be added to a project in a few ways. There's the obvious one::

```
    pip install boltons
```

Then dozens of boltons are just an import away::

```python
    from boltons.cacheutils import LRU
    my_cache = LRU()
```

However, due to the nature of utilities, application developers might
want to consider other options. Boltons is pure-Python and has no
dependencies. See the [Integration][integration] section of the docs
for more details.

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
