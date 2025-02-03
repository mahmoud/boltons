# boltons Changelog

Since February 20, 2013 there have been 45 releases and 1492 commits
for an average of one 33-commit release about every 9 weeks. Versions
are named according to the [CalVer](https://calver.org) versioning
scheme (`YY.MINOR.MICRO`).

## 25.0.0

_(February 2, 2025)_

- Added Python 3.13 support
- Replace deprecated `utcnow()`
- Add fsync to [`fileutils.atomic_save`][fileutils.atomic_save]
- Add [`fileutils.rotate_file`][fileutils.rotate_file]

## 24.1.0

_(November 1, 2024)_

- Added `max_depth` parameter to [`fileutils.iter_find_files`][fileutils.iter_find_files]
- Added `enter` parameter to [`iterutils.research`][iterutils.research] to support traversing custom data types
- Add optional print tracing for [`iterutils.remap`][iterutils.remap] for easier debugging
- Fixed [`typeutils.Sentinel`][typeutils.make_sentinel] copy behavior to return self
- Tentative Python 3.13 support ([#365][i365], [#366][i366])

[i365]: https://github.com/mahmoud/boltons/issues/365
[i366]: https://github.com/mahmoud/boltons/issues/366

## 24.0.0

Per the RFC in issue [#365][i339], boltons is now **Python 3 only**. 3.7+ for now.
If you're a Python 2 user, feel free to pin at `boltons<24.0.0`.

Other minor changes:

- Added Python 3.12 support ([#361][i361])
- Fix [dictutils.OneToOne][dictutils.OneToOne]'s `update()` behavior with empty iterables

[i339]: https://github.com/mahmoud/boltons/issues/339
[i361]: https://github.com/mahmoud/boltons/issues/361

## 23.1.1

_(November 1, 2023)_

Tiny release to include more test files in the sdist (source distribution) on PyPI.

## 23.1.0

_(October 31, 2023)_

- Add `fill`/`end` parameters for [`iterutils.windowed`][iterutils.windowed] and [`iterutils.pairwise`][iterutils.pairwise], respectively ([#350][i350])
- Fix cache eviction for [`cacheutils.LRU`][cacheutils.LRU] ([#348][i348])
- Fix OrderedMultiDict (OMD) pickleability under Py3 ([#337][i337])
- `funcutils.copy_function` maintains kw-only defaults ([#336][i336])
- Support OMD `ior` ([#341][i341])

[i350]: https://github.com/mahmoud/boltons/issues/350
[i348]: https://github.com/mahmoud/boltons/issues/348
[i341]: https://github.com/mahmoud/boltons/issues/341
[i337]: https://github.com/mahmoud/boltons/issues/337
[i336]: https://github.com/mahmoud/boltons/issues/336
[cacheutils.LRU]: http://boltons.readthedocs.org/en/latest/cacheutils.html#boltons.cacheutils.LRU
[iterutils.windowed]: http://boltons.readthedocs.org/en/latest/iterutils.html#boltons.iterutils.windowed
[iterutils.pairwise]: http://boltons.readthedocs.org/en/latest/iterutils.html#boltons.iterutils.pairwise

## 23.0.0

_(February 19, 2023)_

- Overdue update for Python 3.10 and 3.11 support ([#294][i294], [#303][i303], [#320][i320], [#323][i323], [#326][i326]/[#327][i327])
- Add [iterutils.chunk_ranges][iterutils.chunk_ranges] ([#312][i312])
- Improvements to `SpooledBytesIO`/`SpooledStringIO` ([#305][i305])
- Bugfix for infinite daterange issue when start and stop is the same ([#302][i302])
- Fix `Bits.as_list` behavior ([#315][i315])

  21.0.0

---

_(May 16, 2021)_

- Fix [OMD][dictutils.OrderedMultiDict].addlist when the added list is empty
- Add [funcutils.noop][funcutils.noop], satisfying [PEP 559](https://www.python.org/dev/peps/pep-0559/)
- Support lists for [iterutils.bucketize][iterutils.bucketize]
- Python 3.9 test fixes for OMD (PEP 584, see [#271][i271])
- Make [typeutils.make_sentinel][typeutils.make_sentinel] more pickleable
- [jsonutils.reverse_iter_lines][jsonutils.reverse_iter_lines] now works on Py3 and Windows

[jsonutils.reverse_iter_lines]: http://boltons.readthedocs.org/en/latest/jsonutils.html#boltons.jsonutils.reverse_iter_lines
[funcutils.noop]: https://boltons.readthedocs.io/en/latest/funcutils.html#boltons.funcutils.noop
[i271]: https://github.com/mahmoud/boltons/issues/271

## 20.2.1

_(August 11, 2020)_

- Improve import time of [iterutils][iterutils] by deferring hashlib/socket imports
- Add custom `repr` parameter to [funcutils.format_invocation][funcutils.format_invocation]

  20.2.0

---

_(June 21, 2020)_

- Added [iterutils.lstrip][iterutils.lstrip], [iterutils.rstrip][iterutils.rstrip], [iterutils.strip][iterutils.strip]
- More robust and complete [strutils.strip_ansi][strutils.strip_ansi]
- Add [iterutils.untyped_sorted][iterutils.untyped_sorted]
- Fixes to [IndexedSet][IndexedSet] rsub and index methods
- Expose text mode flag in [fileutils.AtomicSaver][fileutils.AtomicSaver]
- Add [strutils.int_list_complement][strutils.int_list_complement] and [strutils.int_list_to_int_tuples][strutils.int_list_to_int_tuples] to the _int_list_ suite.
- Docs: intersphinx links finally point to Python 3 docs

  20.1.0

---

_(March 29, 2020)_

- Add [funcutils.update_wrapper][funcutils.update_wrapper], used to
  make a wrapper function reflect various aspects of the wrapped
  function's API.
- Fix [FunctionBuilder][FunctionBuilder] handling of functions without `__module__`
- Add `partial` support to [FunctionBuilder][FunctionBuilder]
- Fix [NetstringSocket][socketutils.NetstringSocket]'s handling of arguments in `read_ns`
- Fix [IndexedSet][IndexedSet]'s `index()` method to account for removals
- Add `seekable`, `readable`, and `writable` to SpooledIOBase
- Add a special case to `singularize`
- Fix various warnings for Py3.9

  20.0.0

---

_(January 8, 2020)_

- New module [pathutils][pathutils]:
  - [pathutils.augpath][pathutils.augpath] augments a path by modifying its components
  - [pathutils.shrinkuser][pathutils.shrinkuser] inverts :func:`os.path.expanduser`.
  - [pathutils.expandpath][pathutils.expandpath] shell-like environ and tilde expansion
- add `include_dirs` param to [fileutils.iter_find_files][fileutils.iter_find_files]
- Make [funcutils.format_invocation][funcutils.format_invocation] more deterministic
- add [strutils.unwrap_text][strutils.unwrap_text] which does what you think to wrapped text
- Py3 fixes
  - [iterutils.chunked][iterutils.chunked] to work with the `bytes` type ([#231][i231])
  - [cacheutils.ThresholdCounter][cacheutils.ThresholdCounter]'s `get_common_count()`

[i231]: https://github.com/mahmoud/boltons/issues/231
[pathutils]: https://boltons.readthedocs.io/en/latest/pathutils.html
[pathutils.augpath]: https://boltons.readthedocs.io/en/latest/pathutils.html#boltons.pathutils.augpath
[pathutils.augpath]: https://boltons.readthedocs.io/en/latest/pathutils.html#boltons.pathutils.augpath
[pathutils.shrinkuser]: https://boltons.readthedocs.io/en/latest/pathutils.html#boltons.pathutils.shrinkuser
[pathutils.expandpath]: https://boltons.readthedocs.io/en/latest/pathutils.html#boltons.pathutils.expandpath
[strutils.unwrap_text]: https://boltons.readthedocs.io/en/latest/strutils.html#boltons.strutils.unwrap_text

## 19.3.0

_(October 28, 2019)_

Three funcutils:

- [funcutils.format_invocation][funcutils.format_invocation] for formatting simple function calls `func(pos1, pos2, kw_k=kw_v)`
- [funcutils.format_exp_repr][funcutils.format_exp_repr] for formatting a repr like `Type(pos, kw_k=kw_v)`
- [funcutils.format_nonexp_repr][funcutils.format_nonexp_repr] for formatting a repr like `<Type k=v>`

[funcutils.format_invocation]: https://boltons.readthedocs.io/en/latest/funcutils.html#boltons.funcutils.format_invocation
[funcutils.format_exp_repr]: https://boltons.readthedocs.io/en/latest/funcutils.html#boltons.funcutils.format_exp_repr
[funcutils.format_nonexp_repr]: https://boltons.readthedocs.io/en/latest/funcutils.html#boltons.funcutils.format_nonexp_repr

## 19.2.0

_(October 19, 2019)_

A bunch of small fixes and enhancements.

- [tbutils.TracebackInfo][tbutils.TracebackInfo]'s from_frame now respects `level` arg
- [OrderedMultiDict.sorted()][OrderedMultiDict.sorted] now maintains all items, not just the most recent
- [setutils.complement()][setutils.complement] now supports `__rsub__` for better interop with the builtin `set`
- [FunctionBuilder][FunctionBuilder] fixed a few py3 warnings related to inspect module usage (`formatargspec`)
- [iterutils.bucketize][iterutils.bucketize] now takes a string key which works like an attribute getter, similar to other iterutils functions
- Docstring fixes across the board
- CI fixes for Travis default dist change

[OrderedMultiDict.sorted]: http://boltons.readthedocs.org/en/latest/dictutils.html#boltons.dictutils.OrderedMultiDict.sorted

## 19.1.0

_(February 28, 2019)_

Couple of enhancements, couple of cleanups.

- [queueutils][queueutils] now supports float-based priorities ([#204][i204])
- [FunctionBuilder][funcutils.FunctionBuilder] has a new
  `get_arg_names()` method, and its `get_defaults_dict()` method
  finally includes kwonly argument defaults.
- [strutils.gzip_bytes][strutils.gzip_bytes] arrives to match
  [strutils.gunzip_bytes][strutils.gunzip_bytes]

[i204]: https://github.com/mahmoud/boltons/issues/204

## 19.0.1

_(February 12, 2019)_

Quick release to enhance [FunctionBuilder][funcutils.FunctionBuilder]
and [funcutils.wraps][funcutils.wraps] to maintain function
annotations on Python 3+. ([#133][i133], [#134][i134], [#203][i203])

[i133]: https://github.com/mahmoud/boltons/issues/133
[i134]: https://github.com/mahmoud/boltons/issues/134
[i203]: https://github.com/mahmoud/boltons/issues/203

## 19.0.0

_(February 10, 2019)_

A very big release indeed, perhaps the biggest yet. A big, big thank you to all the contributors!

- New types and utilities
  - [dictutils.ManyToMany][dictutils.ManyToMany] arrives, to complement [dictutils.OneToOne][dictutils.OneToOne]
  - [dictutils.FrozenDict][dictutils.FrozenDict] brings immutable mapping to a module near you ([#105][i105])
  - [setutils.complement()][setutils.complement] introduces "negative" sets, useful for exclusion and many other set operations
  - [iterutils.soft_sorted()][iterutils.soft_sorted] allows for looser, more flexible sorting of sequences
  - [iterutils.flatten_iter()][iterutils.flatten_iter] and [iterutils.flatten()][iterutils.flatten], to collapse nested iterables. ([#118][i118])
  - [mathutils.Bits][mathutils.Bits] type for representing a bitstring and translating
    between integer, bytestring, hex, and boolean sequence representations.
- funcutils improvements
  - [FunctionBuilder][funcutils.FunctionBuilder] and [funcutils.wraps][funcutils.wraps] now support coroutines/async ([#194][i194])
  - [FunctionBuilder.add_arg()][funcutils.FunctionBuilder.add_arg] allows the addition of arguments to the signature, to match [FunctionBuilder.remove_arg()][funcutils.FunctionBuilder.remove_arg] ([#201][i201])
  - Similarly [funcutils.wraps()][funcutils.wraps] now takes an "expected" argument, to complement "injected" ([#161][i161])
- Other bugfixes and improvements
  - [cacheutils.LRI][cacheutils.LRI] is now threadsafe and correctly evicts when duplicate keys are added ([#155][i155], [#157][i157])
  - [dictutils.subdict()][dictutils.subdict] now does its best to return the same type of dictionary it was passed.
  - [urlutils][urlutils] now has better IPv6 support and URL can be used more natively like a string
  - Improve singularization in [strutils][strutils]
  - Fix some deprecation warnings in Python 3.7 ([#165][i165], [#196][i196])
  - Document the change in dict constructor behavior affecting [dictutils.OMD][dictutils.OMD] under Python 3.7+ ([#179][i179])

[i105]: https://github.com/mahmoud/boltons/issues/105
[i118]: https://github.com/mahmoud/boltons/issues/118
[i155]: https://github.com/mahmoud/boltons/issues/155
[i157]: https://github.com/mahmoud/boltons/issues/157
[i161]: https://github.com/mahmoud/boltons/issues/161
[i165]: https://github.com/mahmoud/boltons/issues/165
[i179]: https://github.com/mahmoud/boltons/issues/179
[i194]: https://github.com/mahmoud/boltons/issues/194
[i195]: https://github.com/mahmoud/boltons/issues/195
[i196]: https://github.com/mahmoud/boltons/issues/196
[i201]: https://github.com/mahmoud/boltons/issues/201

## 18.0.1

_(August 29, 2018)_

A few bugfixes and a handy text utility.

- Add MultiSub for multiple string substitutions in a single call
  ([#162][i162])
- `tableutils.Table.to_text()` is more Markdown compatible
- Add LICENSE to package ([#164][i164])
- `atomic_save` works better with `overwrite=True` ([#161][i161])
- Reduced memory footprint on `tbutils._DeferredLine` with `__slots__`

  18.0.0

---

_(March 2, 2018)_

- Add `<thead>` and `<tbody>` structure to tableutils.Table HTML
  output, which helps with styling and other functionality (e.g.,
  jQuery datatables).
- Add [dictutils.subdict()][dictutils.subdict] to get a filtered version of a dictionary
  based on a subset of keys. ([#150][i150])
- Add beta version of cacheutils.MinIDMap.

  17.2.0

---

_(December 16, 2017)_

A big release with a lot of features and bugfixes, big and small. Just
in time for the holidays!

- Better handling of `file` and `file`-like objects in [remap][iterutils.remap]'s `default_enter`
- Fix line-by-line iteration in [ioutils][ioutils] types
- Change [strutils.slugify][strutils.slugify] to always output at
  least a single-character slug (in cases of
  all-punctuation/whitespace inputs).
- Fix [DeferredValue][formatutils.DeferredValue] caching in [formatutils][formatutils]
- Add [OneToOne][dictutils.OneToOne] to [dictutils][dictutils]
- Add [MultiFileReader][ioutils.MultiFileReader] to [ioutils][ioutils] (see [#135][i135])
- Support passing `dir` argument to [ioutils][ioutils] SpooledIO types
- fix default arguments for [mathutils.clamp][mathutils.clamp] (see [#128][i128])
- Add [iterutils.research][iterutils.research], a
  [remap][iterutils.remap]-based recursive search function for nested
  data
- Improved and expanded [urlutils.SCHEME_PORT_MAP][urlutils.SCHEME_PORT_MAP]
- Simplify [urlutils.find_all_links][urlutils.find_all_links] signature

  17.1.0

---

_(February 27, 2017)_

Add urlutils module, with URL type and find_all_links function. also
update Sentinel for Python 3 falsiness

- Add urlutils module, complete with RFC3986-compliant `URL` type
- Also add `urlutils.find_all_links` function, which heuristically
  finds all links in plaintext, and creates URLs out of them.
- Update typeutils.Sentinel to be appropriately falsy on Python 3

  17.0.0

---

_(January 24, 2017)_

Several tweaks and enhancements to ring in the new year.

- [tbutils][tbutils] objects like the
  [ExceptionInfo][tbutils.ExceptionInfo] are now more easily
  JSON-serializable thanks to a tweak to [Callpoint][tbutils.Callpoint].
- SpooledIO objects like
  [ioutils.SpooledBytesIO][ioutils.SpooledBytesIO] are now
  `bool`-able.
- [iterutils.bucketize][iterutils.bucketize] gains the
  `value_transform` and `key_filter` arguments.
- [cachedproperty][cacheutils.cachedproperty] properly maintains
  docstring
- [funcutils.wraps][funcutils.wraps] maintains a reference to the
  wrapped function with `__wrapped__` attribute.
- A bit of cleanup to be backwards compatible to Python 3.3

  16.5.1

---

_(November 6, 2016)_

Mostly bug fixes and various tweaks, optimizations, and
documentation. Also added a bit of functionality in the form of
[ioutils][ioutils] and some GUID stuff.

- Add [ioutils][ioutils] with
  [SpooledStringIO][ioutils.SpooledStringIO] and
  [SpooledBytesIO][ioutils.SpooledBytesIO], two in-memory file-like
  objects, like the stdlib [StringIO][StringIO], except that they
  automatically spill over to disk when they reach a configurable
  size.
- Add [iterutils.GUIDerator][iterutils.GUIDerator] and
  [iterutils.SequentialGUIDerator][iterutils.SequentialGUIDerator],
  two methods of getting random iterables.
- Add [mathutils.clamp][mathutils.clamp], a combined min-max function,
  like numpy's clip.
- Optimized [iterutils.first][iterutils.first].
- Enabled spillover kwargs in [funcutils.wraps][funcutils.wraps]
- fix for default [remap][iterutils.remap] set support, fixes [#84][i84]
- improving and testing exceptions around classmethod and staticmethod
  for [funcutils.wraps][funcutils.wraps] and
  [FunctionBuilder][funcutils.FunctionBuilder], fixes [#86][i86] to
  the degree possible.

  16.5.0

---

_(July 16, 2016)_

A few minor changes, and medium-sized breaking change to
[cacheutils][cacheutils].

- [cacheutils][cacheutils] caching decorators now take the
  function/method into account by default. This was done by adding the
  scoped argument to [@cached][cacheutils.cached] and
  [@cachedmethod][cacheutils.cachedmethod] (and removing selfish from
  cachedmethod). also fixed a bug in a cachedmethod test, as well as
  added docs for scoped and key arguments. all of this to fix [#83][i83].
- [tableutils.Table][tableutils.Table] cell html can be customized by
  overriding `get_cell_html` method.
- [funcutils.total_ordering][funcutils.total_ordering], a
  [functools.total_ordering][functools.total_ordering] backport for
  python 2.6.
- [funcutils.FunctionBuilder][funcutils.FunctionBuilder] function
  names are now configurable.

  16.4.1

---

_(June 14, 2016)_

This release primarily contains several [statsutils][statsutils] updates.

- The biggest change was the addition of
  [Stats.format_histogram][statsutils.Stats.format_histogram] complete
  with Freedman bin selection and other useful options.
- Added inter-quartile range (iqr) to [statsutils.Stats][statsutils.Stats]
- Adding mad (median absolute deviation) to
  [Stats.describe][statsutils.Stats.describe], since median and
  std_dev were already there.

  16.4.0

---

_(June 8, 2016)_

another significant release, thanks to the addition of funcutils.wraps
and funcutils.FunctionBuilder. also iterutils.chunked speedup, and
tbutils.ParsedException.to_string.

- [funcutils.wraps][funcutils.wraps]: Just like functools.wraps, but
  can preserve the function signature as well.
- [funcutils.FunctionBuilder][funcutils.FunctionBuilder]: The basis
  for [funcutils.wraps][funcutils.wraps], this full-featured type
  enables programmatically creating functions, from scratch or from
  existing functions. Supports all Python 2 and 3 function features.
- [ecoutils][ecoutils]: Python 2.4 and 2.5 support.
- [iterutils][iterutils]: optimize
  [iterutils.chunked_iter][iterutils.chunked_iter] (2-5x faster
  depending on runtime). [See #79][i79].
- [tbutils][tbutils]: add the
  [ParsedException.to_string][tbutils.ParsedException.to_string]
  method, to convert parsed exceptions back into strings, possibly
  after manipulation
- switch FunctionBuilder on Python 2 to be congruent with Python 3
  (keywords attribute renamed to varkw, preview users might have to
  adjust)

## 16.3.1

_(May 24, 2016)_

Just a couple of [ecoutils][ecoutils] follow-ons, removing uuid
dependency and adding the ability to scrub identifiable data.

## 16.3.0

_(May 23, 2016)_

Big, big update. Lots of additions, a few bugfixes.

- [ecoutils][ecoutils] - Python runtime/environment profile generator
- [timeutils.strpdate][timeutils.strpdate] - like datetime.datetime.strpdate but for date
- [timeutils.daterange][timeutils.daterange] - like range() but for datetime.date objects
- [strutils.parse_int_list][strutils.parse_int_list]
  and [strutils.format_int_list][strutils.format_int_list]
- [cacheutils][cacheutils]
  - [cachedproperty][cacheutils.cachedproperty]
  - [cacheutils.cachedmethod][cacheutils.cachedmethod]
  - [cacheutils.cached][cacheutils.cached] now accepts a callable, as well.
  - `cacheutils.make_cache_key` is now public, should others need it
- [statsutils.Stats][statsutils.Stats] update, several new methods,
  including [Stats.describe][statsutils.Stats.describe]
- A few [socketutils][socketutils] platform tweaks
- `debugutils.wrap_trace` preview

  16.2.2

---

_(May 3, 2016)_

many small tweaks to socketutils.BufferedSocket, including optional
inclusion of the delimiter in recv_until. also undid the enabling of bak
files with AtomicSaver on windows

- Small [socketutils.BufferedSocket][socketutils.BufferedSocket] tweaks
  - make recv_until conditionally return the delimiter (by default it
    does not). also fix a NetstringException inheritance typo
  - [socketutils][socketutils]: rename BufferedSocket.recv_lock to
    \_recv_lock, and same for send_lock.
  - add a bunch of simple passthrough methods to better fill out
    socket's API
  - add .fileno/.close/.shutdown to [socketutils.BufferedSocket][socketutils.BufferedSocket]
  - added type/family/proto
    [socketutils.BufferedSocket][socketutils.BufferedSocket]
    passthrough properties
  - BufferedSocket: also lock on .shutdown()
  - adding an rbuf_unconsumed attribute for post-close debugging, per
    @doublereedkurt's request
  - `getsendbuffer()` returns a bytestring and `recv_size()` uses the proper
    `._recvsize` on the first socket fetch
- [fileutils.AtomicSaver][fileutils.AtomicSaver]: revert bak file as
  it was causing confusion, per [nvie/pip-tools#351](https://github.com/nvie/pip-tools/issues/351)

## 16.2.1

_(April 29, 2016)_

This version sees the soft debut of [socketutils][socketutils], which
includes wrappers and tools for working with the built-in socket. A
lot of [socketutils.BufferedSocket][socketutils.BufferedSocket] changes.

- [BufferedSocket.recv_until][socketutils.BufferedSocket.recv_until] now
  supports multibyte delimiters and also includes the delimiter in its returns.
- Better BufferedSocket timeout discipline throughout.
- Various BufferedSocket argument name changes, _maxbytes_ became
  _maxsize_, _n_ became _size_, _marker_ became _delimiter_, etc.
- [BufferedSocket][socketutils.BufferedSocket] BufferedSocket became
  threadsafe
- [BufferedSocket.recv][socketutils.BufferedSocket.recv] now always returns the
  contents of the internal buffer before doing a socket call.
- [BufferedSocket.recv_close][socketutils.BufferedSocket.recv_close] now exists
  to receive until the sending end closes the connection.
- Can now pass _recvsize_ to
  [BufferedSocket][socketutils.BufferedSocket] constructor to tune
  the size passed to the lower-level recv call.
- [socketutils][socketutils] got documented and tested.

## 16.2.0

_(April 18, 2016)_

adding shell args escaper-joiners to strutils (escape_shell_args,
args2cmd, args2sh) as well as a rare breaking fix to
[iterutils.pairwise][iterutils.pairwise].

- Argument joiners, functions to join command line arguments in
  context-appropriate ways:
  - [strutils.escape_shell_args][strutils.escape_shell_args]
  - [strutils.args2cmd][strutils.args2cmd]
  - [strutils.args2sh][strutils.args2sh]
- BREAKING: finally fixing
  [iterutils.pairwise][iterutils.pairwise]. pairwise used to call to
  `chunked`, now it calls to `windowed`. `pairwise([1, 2, 3, 4])` no
  longer returns `[(1, 2), (3, 4)]`. Instead, it returns
  `[(1, 2), (2, 3), (3, 4)]`, which is what I always mean when I say
  pairwise, but not what the original contributor implemented.
- Adding a universal wheel distribution option!

## 16.1.1

_(March 6, 2016)_

Added [iterutils.same][iterutils.same], improvement of Windows
[fileutils.AtomicSaver][fileutils.AtomicSaver] behavior for old
filesystems, bugfix on [strutils.is_uuid][strutils.is_uuid], expansion
of [strutils.pluralize][strutils.pluralize], new trove classifiers and
docs improvements!

- [fileutils.replace][fileutils.replace]: use bak file option for
  win32 ReplaceFile for slightly better corner case coverage on less
  featureful filesystems
- [strutils.pluralize][strutils.pluralize]: Add more irregular plurals
- [strutils.is_uuid][strutils.is_uuid]: Catch un-parsable UUIDs.
- [iterutils.same][iterutils.same]: Return `True` when all values in
  iterable are the same.

## 16.1.0

_(February 24, 2016)_

The centerpiece of this release is highly improved Windows support for
[fileutils.atomic_save][fileutils.atomic_save] via
[ReplaceFile](https://msdn.microsoft.com/en-us/library/windows/desktop/aa365512%28v=vs.85%29.aspx)
system call. This functionality is also made available directly via
[fileutils.replace][fileutils.replace], which is akin to Python 3.3+'s
[os.replace][os.replace], except that `os.replace`'s approach has
[arguably poorer behavior and atomicity](http://stupidpythonideas.blogspot.com/2014/07/getting-atomic-writes-right.html)
compared to `fileutils.replace`.

Also, a couple new strutils, and
[iterutils.backoff][iterutils.backoff] grew a jitter argument.

- [iterutils.backoff][iterutils.backoff] now supports start=0
- More comprehensive [iterutils.backoff][iterutils.backoff] argument checking/validation
- [fileutils.replace][fileutils.replace] and
  [fileutils.atomic_rename][fileutils.atomic_rename] are now public
  functions in [fileutils][fileutils] with cross-platform implementations ([discussion here](https://github.com/mahmoud/boltons/issues/60))
- [tableutils.Table][tableutils.Table]s have a metadata argument and
  attribute for miscellaneous metadata.
- [strutils.is_ascii][strutils.is_ascii] and
  [strutils.is_uuid][strutils.is_uuid]: About as straightforward as
  they are handy.
- Tox testing improvements

## 16.0.1

_(January 24, 2016)_

DummyFile, Table.metadata, better exception handling, and in-progress
iterutils.get_path

- Small format fix in [iterutils.one][iterutils.one] for None
- Initial implementation of
  [fileutils.DummyFile][fileutils.DummyFile], which allows for easy
  no-op file handling without restructuring code. Sort of like a
  dummy RLock for systems without threading, if you've seen those.
- avoid catching BaseException in all boltons
- better error handling in iterutils.get_path

## 16.0.0

One important fix and one small but handy string function.

- Fixed an [LRU][cacheutils.LRU] bug related to the 15.1.1
  refactor. Also enhanced LRU testing with doubly-linked list
  invariant enforcement.
- Added [strutils.indent][strutils.indent], the counterpart to
  [textwrap.dedent](https://docs.python.org/2/library/textwrap.html#textwrap.dedent).

  15.1.1

---

_(November 18, 2015)_

A lot of bugfixes and docfixes in 15.1.1.

updated AtomicSaver for better permissions handling, update
BufferedSocket message sending, beta version of iterutils.get_path,
several docs fixes, Stats zscore and cache bugfix, and an LRU refactor
with significantly improved behavior and code factoring.

- Updated [fileutils.AtomicSaver][fileutils.AtomicSaver] handling of
  filesystem permissions to be simpler and more secure. This also
  merges `dest_perms` and `part_perms` arguments to AtomicSaver and
  atomic_save.
- Fix large message sending with [socketutils.BufferedSocket][socketutils.BufferedSocket]
- [strutils.iter_splitlines][strutils.iter_splitlines] is now in the docs.
- [cacheutils][cacheutils]: now imports RLock from the right place for python 2
- [statsutils][statsutils]: Only `delattr` when `hasattr` in
  [Stats.clear_cache][statsutils.Stats.clear_cache]
- [statsutils.Stats][statsutils.Stats]: Add
  [Stats.get_zscore][statsutils.Stats.get_zscore] to support
  calculating the [z-score][zscore] (see also: t-statistic)
- [cacheutils.LRU][cacheutils.LRU]: Massive refactor of the backing
  linked list for better handling of duplicate data in the
  cache. More aggressive locking and better `__eq__`

## 15.1.0

_(September 23, 2015)_

Reached the first release version of
[iterutils.remap][iterutils.remap](), fully tested and
documented. Also a couple of tweaks to expose the
[iterutils.unique][iterutils.unique] docs.

## 15.0.2

_(September 9, 2015)_

a couple [dictutils.OMD][dictutils.OMD] fixes to
[dictutils.OMD.pop][dictutils.OMD.pop] and
[dictutils.OMD.popall][dictutils.OMD.popall] to make them consistent
with the docstrings. and the accompanying tests of course.

- fix [dictutils.OMD.setdefault][dictutils.OMD.setdefault] to default
  to None and not empty list, per documentation (and add a test to the
  same effect)

  15.0.1

---

_(August 27, 2015)_

- Added
  [OrderedMultiDict.sortedvalues()][OrderedMultiDict.sortedvalues],
  which returns a copy of the OMD with sublists within a keyspace
  sorted.
- Fixing a bug in
  [dictutils.OrderedMultiDict][dictutils.OrderedMultiDict]'s addlist
  method that caused values to be added multiple times.
- Fixing a [iterutils.backoff][iterutils.backoff] string identity check

[OrderedMultiDict.sortedvalues]: http://boltons.readthedocs.org/en/latest/dictutils.html#boltons.dictutils.OrderedMultiDict.sortedvalues

## 15.0.0

_(August 19, 2015)_

Finally the 15.0 major release. All passing PRs and feature requests
from the first wave addressed and closed. tzutils merged into
timeutils. AtomicSaver approach and API much improved. Several other
features added:

- [iterutils.backoff][iterutils.backoff] and [iterutils.backoff_iter][iterutils.backoff_iter] for exponential backoff
- [iterutils.frange][iterutils.frange] and [iterutils.xfrange][iterutils.xfrange] for floating point range generation
- Slightly more permissive [jsonutils.JSONLIterator][jsonutils.JSONLIterator] blank line ignoring
- [strutils.iter_splitlines][strutils.iter_splitlines] for lazily getting lines from a larger string
- [timeutils.dt_to_timestamp][timeutils.dt_to_timestamp], per the long-lived PR [#13][i13].
- Merged tzutils into timeutils
- [fileutils.AtomicSaver][fileutils.AtomicSaver] rewrite and redoc
- -teens support for [strutils.ordinalize][strutils.ordinalize]
- made [iterutils.one][iterutils.one] consistent with [iterutils.first][iterutils.first]

## 0.6.6

_(July 31, 2015)_

Fix atomic saving open-file issue for Windows.

- Patch for AtomicSaver on Windows. Full rewrite comes in 15.0.0.
- [strutils.gunzip_bytes][strutils.gunzip_bytes] for decompressing a gzip bytestring

## 0.6.5

_(July 30, 2015)_

BufferedSocket work, html2text, pairwise shortcut, is_container, plural
typo fix, [timeutils.isoparse][timeutils.isoparse], [cacheutils.ThresholdCounter][cacheutils.ThresholdCounter], and lots of
testing

- Add [iterutils.first][iterutils.first] function
- Add [cacheutils.ThresholdCounter][cacheutils.ThresholdCounter]
- Add JSONL verification to jsonutils
- Add [timeutils.isoparse][timeutils.isoparse]
- Add [strutils.html2text][strutils.html2text] and [strutils.HTMLTextExtractor][strutils.HTMLTextExtractor]
- Fix [strutils.pluralize][strutils.pluralize] (indeces -> indices, per [#41][i41])
- Add [iterutils.is_container][iterutils.is_container] function
- Fixed a small formatting bug in [tbutils.ExceptionInfo][tbutils.ExceptionInfo] that added
  an extra 'builtins.' for builtin exceptions under python 3
- Added tests for many modules
- Create [iterutils.pairwise][iterutils.pairwise] shortcuts for pairwise chunks since
  pairs (key/val) are common
- Additional 2.6 compatibility and tests
- Fixed CachedInstancePartial to be Python 3 friendly without breaking
  PyPy.
- Made formatutils Python 3 compatible
- Rename sockutils to socketutils and other changes

## 0.6.4

_(May 10, 2015)_

Fixed multiline exception message handling in ParsedException. added
mathutils. adding a tentative version of socketutils. fix LRU.popitem. fix
OMD.**eq**.

- Fix a bug where [dictutils.OrderedMultiDict][dictutils.OrderedMultiDict]'s **eq** would fail
  with non-iterable objects of comparison
- Fixed `LRU.popitem` to return a key value pair
- Added mathutils with [mathutils.ceil][mathutils.ceil] and [mathutils.floor][mathutils.floor]
  implementations that can search a fixed set of choices using the
  bisect module.
- Fix [excutils.ParsedException][excutils.ParsedException] so exception message would not start
  with whitespace
- Fix multiline exception messages
- Adding [socketutils.BufferedSocket][socketutils.BufferedSocket] and [socketutils.NetstringSocket][socketutils.NetstringSocket]

## 0.6.3

_(April 20, 2015)_

Add typeutils, remove compat.py, make ParsedException work with eval()ed
code

- Properly parse tracebacks with missing source. Resolves [#30][i30]
- Tweak the docs for [typeutils.get_all_subclasses][typeutils.get_all_subclasses]
- Moved [typeutils.make_sentinel][typeutils.make_sentinel] into typeutils and removed the
  confusing compat module
- Add in typeutils with modifications per the caveats of [#15][i15]
- Added function [iterutils.one][iterutils.one]

## 0.6.2

_(April 11, 2015)_

Add partial_ordering, fix LRU repr and addition behavior

- Add [funcutils.partial_ordering][funcutils.partial_ordering](), decorator similar to
  functools.total_ordering()
- Fixed [cacheutils.LRU][cacheutils.LRU]'s behavior per [#21][i21]
- Fix [cacheutils.LRU][cacheutils.LRU] repr reversal, fixes [#20][i20]

## 0.6.0

_(April 10, 2015)_

Python 3 support and several community bugfixes. Docs clarifications, too.

- Make boltons Python 3 compatible without any external
  dependencies. All modules are independent and work in Python 2.6,
  2.7, 3.4, and PyPy.
- clarify TracebackInfo.from_current() method gap, per user 'dl\_\_'
  here: http://www.reddit.com/r/Python/comments/321d3o/boltons_over_100_python_utilities/
- Fix the [cacheutils.cached][cacheutils.cached] decorator, adding a sanity test, fixes [#12][i12]
- Fix bytes2human when builtin zip returns iterators
- Simplified logic of [iterutils.chunked][iterutils.chunked]

## 0.5.1

_(April 10, 2015)_

A lot of bugfixes and Python 2.6 and PyPy compatibility changes thanks
to community contributions and encouragement.

- Corrected cases where OMD was not exactly a dropin for OrderedDict
- conditional availability of [gcutils.get_all][gcutils.get_all] based on pypy or cpython, also
  [gcutils.is_tracked][gcutils.is_tracked] was added in 2.7, so making [gcutils.get_all][gcutils.get_all] work with 2.6
- Made namedutils backwards compatibility for python 2.6 best effort
- Fix invalid part_path usage in [fileutils.AtomicSaver][fileutils.AtomicSaver]

## 0.5.0

_(April 9, 2015)_

First publicly released version. The major focus of this release was
docs, docstrings, and Read The Docs.

- Cleared out **init** module for maximum independence
- making [statsutils.median][statsutils.median] use \_get_quantile and add [statsutils.trimean][statsutils.trimean]
- Switching the [statsutils.Stats][statsutils.Stats] type to be more sorted-data oriented, since it's
  only for offline analysis of unordered data
- Made consistent multi-line string formats, as well as usage of the
  term 'builtin' vs 'built-in' (noun vs adjective)
- Instrumented LRI with stats tracking
- Made [timeutils.decimal_relative_time][timeutils.decimal_relative_time] cardinalization optional
- Removed timeutils dependency on strutils
- Made [tbutils.TracebackInfo][tbutils.TracebackInfo] classmethods work with no arguments.
- Renamed ParsedTB to [tbutils.ParsedException][tbutils.ParsedException]
- Made [dictutils.OMD][dictutils.OMD] .get()/.getlist() semantics more consistent.
- finalizing .todict() and adding .sorted() to the [dictutils.OMD][dictutils.OMD]
- Removed osutils and adding a note about utils in general
- Made cacheutils more consistent between LRU and LRI, adding some
  cacheutils docs
- Deprecate osutils, moving its contents into fileutils
- Adding in-process statsutils2, with new DataAnalyzer and
  get_pearson_type (not merged yet)

## 0.4.2

_(March 8, 2015)_

Mostly a dictutils API update (addlist), but also gcutils.

- [dictutils.OMD][dictutils.OMD]: split out addlist() from add(), removing the multi
  kwarg
- adding gcutils with [gcutils.GCToggler][gcutils.GCToggler] and gc.get_all

## 0.4.1

_(February 26, 2015)_

adding mboxutils

- adding mboxutils for handy dandy /var/mail integrations like cronfed

## 0.4.0

_(February 23, 2015)_

updated tbutils, JSONL support, initial cacheutils, atomic writer,
hashtags

- tbutils: Changed the way exceptions are parsed out of tracebacks
- tbutils: Guard against potential linecache issues
- Defined/implemented [iterutils.windowed_iter][iterutils.windowed_iter] corner case behavior
- Added from_path to [fileutils.FilePerms][fileutils.FilePerms]
- Adding [strutils.find_hashtags][strutils.find_hashtags]
- Add ignore patterns to [fileutils.iter_find_files][fileutils.iter_find_files]

## 0.3.0

_(October 19, 2014)_

First alpha release. Practically, everything not mentioned above was
added in this release.

- tbutils: add ContextualTracebackInfo and ContextualExceptionInfo
- cacheutils: a few minor changes to the BasicCache
- update tbutils with some critical bits. still need to add
  convenience method for ExceptionInfo -> default exception print,
  also need to add more docstrings.
- adding initial jsonutils with JSONL support
- added [cacheutils.LRU][cacheutils.LRU]
- added [timeutils.parse_timedelta][timeutils.parse_timedelta]
- fixing iteritems with multi=False in the
  [dictutils.OrderedMultiDict][dictutils.OrderedMultiDict] (should return first key, but last
  value not first)
- debugutils: add pdb excepthook and [debugutils.pdb_on_signal][debugutils.pdb_on_signal]
- add [fileutils.mkdir_p][fileutils.mkdir_p]
- tableutils: add maxlen to table text stuff
- fix date citation for gob's
- adding pure-Python implementation of Gob's algorithm
- fix object header guessing
- namedutils: add namedtuple support
- fix a headers bug in tableutils
- tableutils: add a couple more do-not-recurse types, add
  UnsupportedData exception for better recursion, insert recursive
  entries in-line, improve 'Object' strategy heuristic
- wrap up html tag customization and fix a related bug
- make html configurable via class attributes
- strengthen the max_depth check
- InputType classes are just shorter and clearer, imo
- new from_dict, from_list, from_object, removing old ones. almost
  used a MetaClass for this
- starting new table
- only update the integer for the field being updated
- fixing a verbalization/pronunciation issue
- no regex for better error messages
- being opinionated about some FilePerms things
- adding initial version of fileutils/FilePerms
- update formatutils
- fix a slightly nasty namedlist bug
- make OrderedMultiDict.get()'s default allow singulars
- sync over ExceptionInfo
- add from_current() classmethod with depth option to [Callpoint][tbutils.Callpoint] class
  for easier instantiation
- it's called a numeronym
- add a repr to ParsedTB. A bit verbose, but better than nothing.
- add ParsedTB, which provides the ability to parse tracebacks dumped
  out to logs, the command line, etc.
- improve test output and make assertion that new except hook is the
  same as the builtin.
- update tbutils to use the more-powerful [Callpoint][tbutils.Callpoint] type.
- copy_function
- partially clean up partial stuff
- first version of the namedlist
- fixing up namedtuple, groundwork for namedlist. humorously named
  module.
- embed value in cell for incremental iteration boost on OMD
- reorganize code, add 'default' argument to poplast()
- make key argument optional to OMD.poplast
- rectifying inconsistent names and adjusting respective tests
  accordingly. using smashcase because that's what builtin dict()
  uses.
- fix reverse; missing yield from!
- add initial table biz
- add get_counts
- add [dictutils.OrderedMultiDict.get_inverted][dictutils.OrderedMultiDict.get_inverted]() for those handy reverse lookups
- break out skip list to FastIter OMD + bench
- add [strutils.a10n][strutils.a10n]()
- fix a bug in [dictutils.OrderedMultiDict][dictutils.OrderedMultiDict]'s .add()
- adding initial reimplementation of OMD
- adding some tests to dictutils
- update boltons formatutils to match what's going on in lithoxyl
- remove infer_pos_args() from strutils (already in formatutils)
- add formatutils to boltons
- fix a potential infinite recursion in LocalTZ
- use more explicit names for Local/Constant tzinfo types
- add a basic but handy file finder
- add infer_positional_args() to strutils (from lithoxyl)
- split BasicCache out of dictutils into cacheutils
- update median calculation slightly
- add appropriate stacklevel to deprutils warning
- add an initial version of deprutils (basic utils for facilitating
  deprecation)
- add bytes2human
- first version of some basic timezone utils which came in handy for a
  train scheduling application I wrote (etavta)
- reorder imports for pep8
- redo plain-english relative_time() to have a decimal rounding factor
  and handle future dates
- swap the order of cardinalize()'s arguments after intuiting the
  wrong order a couple times. gotta be consistent, this isn't PHP.
- a weird little relative time approach
- add total_seconds() implementation for Python <2.7, rename
  relative_datetime to relative_time
- add a relative datetime function in a new module: timeutils
- a little more transparency with orderedmultidict's maphistory
- add a test for BasicCache
- add the super simple BasicCache, a size-limited defaultdict-like
  thing
- add a cheesy little splay list construct that can be used for splay-
  like manual reordering for eventual optimization
- traceback utils, first draft
- add [strutils.strip_ansi][strutils.strip_ansi] (need to make a cliutils or something)
- add ansi strip task
- mess with list tuning
- add ordinalize()
- add **all** to statsutils
- add more stats docs and doctests
- add some stats functions
- add unit_len()
- add pluralize/singularize/cardinalize to strutils
- add **all**s all around, clean up imports a bit
- adding license
- add sorted queue type, make it the default
- fix little bug in insert
- inheriting from list necessitates overriding the deprecated **get-,
  **set-, and \_\_del- slice methods
- hacky refactor to have a BasePriorityQueue to make room for
  SortedPriorityQueue with peek_n, etc.
- add a little docstring and update sort method in BarrelList
- add HeapPriorityQueue
- tidy up listutils comments and imports
- move treeutils out of boltons since I don't really think a pure
  python version actually adds much. i'll make an academic one-off
  repo for less practical data structure experiments like that.
- inherit from list
- add reverse() to blist
- add index() to blist
- cheesy **setitem**() for blist
- add **delitem**() to BarrelList
- change the way the in-place sort works with just one list
- tune the list size a bit
- add slicing to BarrelList
- add initial version of BarrelList, a pure-python b-list-y thing to
  approximate O(log(n)) behavior by multiplexing the fast O(n) list
  operations
- switch to new dead index interval approach; the IndexedSet is about
  half the speed of a list in the ultra-pathological case of random
  popping on the low end of the IndexedSet
- made BisectTree's get() defaulting work a bit more like a dict's
- added get_adjacent and miscellaneous to BisectTree
- added a default name and always-falsy **nonzero** to Sentinel
- add pop() for BisectTree and export the generic Tree
- make a bisect tree, because O(n) is still pretttttty fast up to
  about 100k items
- add a little hack to chunked/chunked_iter to make it work nicely
  with strings
- tidy up ki_vs_vi_lrh usage just a titch
- revamp indices behavior (key_size and value_size)
- switch to new multi-key mode
- pretty much done porting insert, delete, balance (the basic
  operations)
- switch to negative refs, arbitrary length nodes
- add sentinel utility thing
- add .index() for list compat, updated exception messages, and added
  a silly test to show off slicing and indexing
- add slicing support and .clear()
- remove ifilter dependency (using generator expression)
- add .reverse and .sort() to IndexedSet, fix bisection related bug
  exposing MISSING (insort requested index, not real_index)
- pretty much all fundy IndexedSet bugs hit and fixed, looks like
- IndexedSet getting much closer
- initial rough draft of IndexedSet with a short docstring and a bunch
  of fixes already (still not workin tho)
- add dictutils (OrderedMultiDict)
- it was a long time coming, but I'm finally halfway happy with this
  wrapped exception
- add uniqueification capabilities
- go back to using **new** and positional arguments
- exception wrapping green path mostly working
- working on a wrapping exception mixin thing for less lossy
  nonraising.
- add asciify and update slugify with ascii flag
- add basic docs and doctests to strutils
- scratch that, regexes still faster
- add under2camel, camel2under, and slugify (and split_punct_ws, which
  is much faster than re-based punctuation splitting)
- python3-compatible doctest for bucketize_bool
- bucketize and bucketize_bool, with docs
- add examples to chunked and chunked_iter
- update split() docs with more examples.
- [iterutils.chunked_iter][iterutils.chunked_iter] and [iterutils.chunked][iterutils.chunked]
- [iterutils.split][iterutils.split] and [iterutils.split_iter][iterutils.split_iter] work

[os.replace]: https://docs.python.org/3/library/os.html#os.replace
[functools.total_ordering]: https://docs.python.org/2/library/functools.html#functools.total_ordering
[StringIO]: https://docs.python.org/2/library/stringio.html
[zscore]: https://en.wikipedia.org/wiki/Standard_score
[cacheutils]: http://boltons.readthedocs.org/en/latest/cacheutils.html
[cacheutils.LRI]: http://boltons.readthedocs.org/en/latest/cacheutils.html#boltons.cacheutils.LRI
[cacheutils.LRU]: http://boltons.readthedocs.org/en/latest/cacheutils.html#boltons.cacheutils.LRU
[cacheutils.ThresholdCounter]: http://boltons.readthedocs.org/en/latest/cacheutils.html#boltons.cacheutils.ThresholdCounter
[cacheutils.cached]: http://boltons.readthedocs.org/en/latest/cacheutils.html#boltons.cacheutils.cached
[cacheutils.cachedmethod]: http://boltons.readthedocs.org/en/latest/cacheutils.html#boltons.cacheutils.cachedmethod
[cacheutils.cachedproperty]: http://boltons.readthedocs.org/en/latest/cacheutils.html#boltons.cacheutils.cachedproperty
[debugutils.pdb_on_signal]: http://boltons.readthedocs.org/en/latest/debugutils.html#boltons.debugutils.pdb_on_signal
[dictutils]: http://boltons.readthedocs.org/en/latest/dictutils.html
[dictutils.OMD]: http://boltons.readthedocs.org/en/latest/dictutils.html#boltons.dictutils.OMD
[dictutils.OMD.pop]: http://boltons.readthedocs.org/en/latest/dictutils.html#boltons.dictutils.OrderedMultiDict.pop
[dictutils.OMD.popall]: http://boltons.readthedocs.org/en/latest/dictutils.html#boltons.dictutils.OrderedMultiDict.popall
[dictutils.OMD.setdefault]: http://boltons.readthedocs.org/en/latest/dictutils.html#boltons.dictutils.OrderedMultiDict.setdefault
[dictutils.OrderedMultiDict]: http://boltons.readthedocs.org/en/latest/dictutils.html#boltons.dictutils.OrderedMultiDict
[dictutils.OrderedMultiDict.get_inverted]: http://boltons.readthedocs.org/en/latest/dictutils.html#boltons.dictutils.OrderedMultiDict.get_inverted
[dictutils.OneToOne]: http://boltons.readthedocs.org/en/latest/dictutils.html#boltons.dictutils.OneToOne
[dictutils.ManyToMany]: http://boltons.readthedocs.org/en/latest/dictutils.html#boltons.dictutils.ManyToMany
[dictutils.FrozenDict]: http://boltons.readthedocs.org/en/latest/dictutils.html#boltons.dictutils.FrozenDict
[dictutils.subdict]: http://boltons.readthedocs.org/en/latest/dictutils.html#boltons.dictutils.subdict
[ecoutils]: http://boltons.readthedocs.org/en/latest/ecoutils.html
[excutils.ParsedException]: http://boltons.readthedocs.org/en/latest/excutils.html#boltons.excutils.ParsedException
[fileutils]: http://boltons.readthedocs.org/en/latest/fileutils.html
[fileutils.replace]: http://boltons.readthedocs.org/en/latest/fileutils.html#boltons.fileutils.replace
[fileutils.rotate_file]: http://boltons.readthedocs.org/en/latest/fileutils.html#boltons.fileutils.rotate_file
[fileutils.atomic_rename]: http://boltons.readthedocs.org/en/latest/fileutils.html#boltons.fileutils.atomic_rename
[fileutils.atomic_save]: http://boltons.readthedocs.org/en/latest/fileutils.html#boltons.fileutils.atomic_save
[fileutils.AtomicSaver]: http://boltons.readthedocs.org/en/latest/fileutils.html#boltons.fileutils.AtomicSaver
[fileutils.FilePerms]: http://boltons.readthedocs.org/en/latest/fileutils.html#boltons.fileutils.FilePerms
[fileutils.iter_find_files]: http://boltons.readthedocs.org/en/latest/fileutils.html#boltons.fileutils.iter_find_files
[fileutils.mkdir_p]: http://boltons.readthedocs.org/en/latest/fileutils.html#boltons.fileutils.mkdir_p
[fileutils.DummyFile]: http://boltons.readthedocs.org/en/latest/fileutils.html#boltons.fileutils.DummyFile
[formatutils]: http://boltons.readthedocs.org/en/latest/formatutils.html
[formatutils.DeferredValue]: http://boltons.readthedocs.org/en/latest/formatutils.html#boltons.fileutils.DeferredValue
[funcutils.FunctionBuilder]: http://boltons.readthedocs.org/en/latest/funcutils.html#boltons.funcutils.FunctionBuilder
[funcutils.FunctionBuilder.remove_arg]: https://boltons.readthedocs.io/en/latest/funcutils.html#boltons.funcutils.FunctionBuilder.remove_arg
[funcutils.FunctionBuilder.add_arg]: https://boltons.readthedocs.io/en/latest/funcutils.html#boltons.funcutils.FunctionBuilder.add_arg
[funcutils.partial_ordering]: http://boltons.readthedocs.org/en/latest/funcutils.html#boltons.funcutils.partial_ordering
[funcutils.total_ordering]: http://boltons.readthedocs.org/en/latest/funcutils.html#boltons.funcutils.total_ordering
[funcutils.update_wrapper]: http://boltons.readthedocs.org/en/latest/funcutils.html#boltons.funcutils.update_wrapper
[funcutils.wraps]: http://boltons.readthedocs.org/en/latest/funcutils.html#boltons.funcutils.wraps
[gcutils.GCToggler]: http://boltons.readthedocs.org/en/latest/gcutils.html#boltons.gcutils.GCToggler
[gcutils.get_all]: http://boltons.readthedocs.org/en/latest/gcutils.html#boltons.gcutils.get_all
[gcutils.is_tracked]: http://boltons.readthedocs.org/en/latest/gcutils.html#boltons.gcutils.is_tracked
[i12]: https://github.com/mahmoud/boltons/issues/12
[i13]: https://github.com/mahmoud/boltons/issues/13
[i15]: https://github.com/mahmoud/boltons/issues/15
[i20]: https://github.com/mahmoud/boltons/issues/20
[i21]: https://github.com/mahmoud/boltons/issues/21
[i30]: https://github.com/mahmoud/boltons/issues/30
[i41]: https://github.com/mahmoud/boltons/issues/41
[i79]: https://github.com/mahmoud/boltons/pull/79
[i83]: https://github.com/mahmoud/boltons/issues/83
[i84]: https://github.com/mahmoud/boltons/issues/84
[i86]: https://github.com/mahmoud/boltons/issues/86
[i128]: https://github.com/mahmoud/boltons/issues/128
[i135]: https://github.com/mahmoud/boltons/issues/135
[i150]: https://github.com/mahmoud/boltons/issues/150
[i161]: https://github.com/mahmoud/boltons/issues/161
[i162]: https://github.com/mahmoud/boltons/issues/162
[i164]: https://github.com/mahmoud/boltons/issues/164
[i294]: https://github.com/mahmoud/boltons/issues/294
[i302]: https://github.com/mahmoud/boltons/issues/302
[i303]: https://github.com/mahmoud/boltons/issues/303
[i305]: https://github.com/mahmoud/boltons/issues/305
[i312]: https://github.com/mahmoud/boltons/issues/312
[i315]: https://github.com/mahmoud/boltons/issues/315
[i320]: https://github.com/mahmoud/boltons/issues/320
[i323]: https://github.com/mahmoud/boltons/issues/323
[i326]: https://github.com/mahmoud/boltons/issues/326
[i327]: https://github.com/mahmoud/boltons/issues/327
[ioutils]: http://boltons.readthedocs.org/en/latest/ioutils.html
[ioutils.MultiFileReader]: http://boltons.readthedocs.org/en/latest/ioutils.html#boltons.ioutils.MultiFileReader
[ioutils.SpooledBytesIO]: http://boltons.readthedocs.org/en/latest/ioutils.html#boltons.ioutils.SpooledBytesIO
[ioutils.SpooledStringIO]: http://boltons.readthedocs.org/en/latest/ioutils.html#boltons.ioutils.SpooledStringIO
[iterutils]: http://boltons.readthedocs.org/en/latest/iterutils.html
[iterutils.backoff]: http://boltons.readthedocs.org/en/latest/iterutils.html#boltons.iterutils.backoff
[iterutils.backoff_iter]: http://boltons.readthedocs.org/en/latest/iterutils.html#boltons.iterutils.backoff_iter
[iterutils.chunked]: http://boltons.readthedocs.org/en/latest/iterutils.html#boltons.iterutils.chunked
[iterutils.chunked_iter]: http://boltons.readthedocs.org/en/latest/iterutils.html#boltons.iterutils.chunked_iter
[iterutils.chunk_ranges]: http://boltons.readthedocs.org/en/latest/iterutils.html#boltons.iterutils.chunk_ranges
[iterutils.first]: http://boltons.readthedocs.org/en/latest/iterutils.html#boltons.iterutils.first
[iterutils.flatten]: http://boltons.readthedocs.org/en/latest/iterutils.html#boltons.iterutils.flatten
[iterutils.flatten_iter]: http://boltons.readthedocs.org/en/latest/iterutils.html#boltons.iterutils.flatten_iter
[iterutils.backoff]: http://boltons.readthedocs.org/en/latest/iterutils.html#boltons.iterutils.backoff
[iterutils.frange]: http://boltons.readthedocs.org/en/latest/iterutils.html#boltons.iterutils.frange
[iterutils.GUIDerator]: http://boltons.readthedocs.org/en/latest/iterutils.html#boltons.iterutils.GUIDerator
[iterutils.SequentialGUIDerator]: http://boltons.readthedocs.org/en/latest/iterutils.html#boltons.iterutils.SequentialGUIDerator
[iterutils.is_container]: http://boltons.readthedocs.org/en/latest/iterutils.html#boltons.iterutils.is_container
[iterutils.bucketize]: http://boltons.readthedocs.org/en/latest/iterutils.html#boltons.iterutils.bucketize
[iterutils.one]: http://boltons.readthedocs.org/en/latest/iterutils.html#boltons.iterutils.one
[iterutils.pairwise]: http://boltons.readthedocs.org/en/latest/iterutils.html#boltons.iterutils.pairwise
[iterutils.same]: http://boltons.readthedocs.org/en/latest/iterutils.html#boltons.iterutils.same
[iterutils.remap]: http://boltons.readthedocs.org/en/latest/iterutils.html#boltons.iterutils.remap
[iterutils.research]: http://boltons.readthedocs.org/en/latest/iterutils.html#boltons.iterutils.research
[iterutils.soft_sorted]: http://boltons.readthedocs.org/en/latest/iterutils.html#boltons.iterutils.soft_sorted
[iterutils.untyped_sorted]: http://boltons.readthedocs.org/en/latest/iterutils.html#boltons.iterutils.untyped_sorted
[iterutils.split]: http://boltons.readthedocs.org/en/latest/iterutils.html#boltons.iterutils.split
[iterutils.split_iter]: http://boltons.readthedocs.org/en/latest/iterutils.html#boltons.iterutils.split_iter
[iterutils.strip]: http://boltons.readthedocs.org/en/latest/iterutils.html#boltons.iterutils.strip
[iterutils.rstrip]: http://boltons.readthedocs.org/en/latest/iterutils.html#boltons.iterutils.rstrip
[iterutils.lstrip]: http://boltons.readthedocs.org/en/latest/iterutils.html#boltons.iterutils.lstrip
[iterutils.unique]: http://boltons.readthedocs.org/en/latest/iterutils.html#boltons.iterutils.unique
[iterutils.windowed_iter]: http://boltons.readthedocs.org/en/latest/iterutils.html#boltons.iterutils.windowed_iter
[iterutils.xfrange]: http://boltons.readthedocs.org/en/latest/iterutils.html#boltons.iterutils.xfrange
[jsonutils.JSONLIterator]: http://boltons.readthedocs.org/en/latest/jsonutils.html#boltons.jsonutils.JSONLIterator
[mathutils.Bits]: http://boltons.readthedocs.org/en/latest/mathutils.html#boltons.mathutils.Bits
[mathutils.ceil]: http://boltons.readthedocs.org/en/latest/mathutils.html#boltons.mathutils.ceil
[mathutils.floor]: http://boltons.readthedocs.org/en/latest/mathutils.html#boltons.mathutils.floor
[mathutils.clamp]: http://boltons.readthedocs.org/en/latest/mathutils.html#boltons.mathutils.clamp
[queueutils]: http://boltons.readthedocs.org/en/latest/queueutils.html
[setutils.complement]: http://boltons.readthedocs.org/en/latest/setutils.html#boltons.setutils.complement
[IndexedSet]: http://boltons.readthedocs.org/en/latest/setutils.html#boltons.setutils.IndexedSet
[socketutils]: http://boltons.readthedocs.org/en/latest/socketutils.html
[socketutils.BufferedSocket]: http://boltons.readthedocs.org/en/latest/socketutils.html#boltons.socketutils.BufferedSocket
[socketutils.BufferedSocket.recv]: http://boltons.readthedocs.org/en/latest/socketutils.html#boltons.socketutils.BufferedSocket.recv
[socketutils.BufferedSocket.recv_until]: http://boltons.readthedocs.org/en/latest/socketutils.html#boltons.socketutils.BufferedSocket.recv_until
[socketutils.BufferedSocket.recv_close]: http://boltons.readthedocs.org/en/latest/socketutils.html#boltons.socketutils.BufferedSocket.recv_close
[socketutils.NetstringSocket]: http://boltons.readthedocs.org/en/latest/socketutils.html#boltons.socketutils.NetstringSocket
[statsutils]: http://boltons.readthedocs.org/en/latest/statsutils.html
[statsutils.Stats]: http://boltons.readthedocs.org/en/latest/statsutils.html#boltons.statsutils.Stats
[statsutils.Stats.clear_cache]: http://boltons.readthedocs.org/en/latest/statsutils.html#boltons.statsutils.Stats.clear_cache
[statsutils.Stats.describe]: http://boltons.readthedocs.org/en/latest/statsutils.html#boltons.statsutils.Stats.describe
[statsutils.Stats.format_histogram]: http://boltons.readthedocs.org/en/latest/statsutils.html#boltons.statsutils.Stats.format_histogram
[statsutils.Stats.get_zscore]: http://boltons.readthedocs.org/en/latest/statsutils.html#boltons.statsutils.Stats.get_zscore
[statsutils.median]: http://boltons.readthedocs.org/en/latest/statsutils.html#boltons.statsutils.median
[statsutils.trimean]: http://boltons.readthedocs.org/en/latest/statsutils.html#boltons.statsutils.trimean
[strutils]: http://boltons.readthedocs.org/en/latest/strutils.html
[strutils.HTMLTextExtractor]: http://boltons.readthedocs.org/en/latest/strutils.html#boltons.strutils.HTMLTextExtractor
[strutils.a10n]: http://boltons.readthedocs.org/en/latest/strutils.html#boltons.strutils.a10n
[strutils.args2cmd]: http://boltons.readthedocs.org/en/latest/strutils.html#boltons.strutils.args2cmd
[strutils.args2sh]: http://boltons.readthedocs.org/en/latest/strutils.html#boltons.strutils.args2sh
[strutils.escape_shell_args]: http://boltons.readthedocs.org/en/latest/strutils.html#boltons.strutils.escape_shell_args
[strutils.find_hashtags]: http://boltons.readthedocs.org/en/latest/strutils.html#boltons.strutils.find_hashtags
[strutils.gzip_bytes]: http://boltons.readthedocs.org/en/latest/strutils.html#boltons.strutils.gzip_bytes
[strutils.gunzip_bytes]: http://boltons.readthedocs.org/en/latest/strutils.html#boltons.strutils.gunzip_bytes
[strutils.html2text]: http://boltons.readthedocs.org/en/latest/strutils.html#boltons.strutils.html2text
[strutils.indent]: http://boltons.readthedocs.org/en/latest/strutils.html#boltons.strutils.indent
[strutils.iter_splitlines]: http://boltons.readthedocs.org/en/latest/strutils.html#boltons.strutils.iter_splitlines
[strutils.ordinalize]: http://boltons.readthedocs.org/en/latest/strutils.html#boltons.strutils.ordinalize
[strutils.pluralize]: http://boltons.readthedocs.org/en/latest/strutils.html#boltons.strutils.pluralize
[strutils.is_ascii]: http://boltons.readthedocs.org/en/latest/strutils.html#boltons.strutils.is_ascii
[strutils.is_uuid]: http://boltons.readthedocs.org/en/latest/strutils.html#boltons.strutils.is_uuid
[strutils.parse_int_list]: http://boltons.readthedocs.org/en/latest/strutils.html#boltons.strutils.parse_int_list
[strutils.format_int_list]: http://boltons.readthedocs.org/en/latest/strutils.html#boltons.strutils.format_int_list
[strutils.int_list_complement]: http://boltons.readthedocs.org/en/latest/strutils.html#boltons.strutils.int_list_complement
[strutils.int_list_to_int_tuples]: http://boltons.readthedocs.org/en/latest/strutils.html#boltons.strutils.int_list_to_int_tuples
[strutils.slugify]: http://boltons.readthedocs.org/en/latest/strutils.html#boltons.strutils.slugify
[strutils.strip_ansi]: http://boltons.readthedocs.org/en/latest/strutils.html#boltons.strutils.strip_ansi
[tableutils]: http://boltons.readthedocs.org/en/latest/tableutils.html
[tableutils.Table]: http://boltons.readthedocs.org/en/latest/tableutils.html#boltons.tableutils.Table
[tbutils]: http://boltons.readthedocs.org/en/latest/tbutils.html
[tbutils.Callpoint]: http://boltons.readthedocs.org/en/latest/tbutils.html#boltons.tbutils.Callpoint
[tbutils.ExceptionInfo]: http://boltons.readthedocs.org/en/latest/tbutils.html#boltons.tbutils.ExceptionInfo
[tbutils.ParsedException]: http://boltons.readthedocs.org/en/latest/tbutils.html#boltons.tbutils.ParsedException
[tbutils.ParsedException.to_string]: http://boltons.readthedocs.org/en/latest/tbutils.html#boltons.tbutils.ParsedException.to_string
[tbutils.TracebackInfo]: http://boltons.readthedocs.org/en/latest/tbutils.html#boltons.tbutils.TracebackInfo
[timeutils.daterange]: http://boltons.readthedocs.org/en/latest/timeutils.html#boltons.timeutils.daterange
[timeutils.decimal_relative_time]: http://boltons.readthedocs.org/en/latest/timeutils.html#boltons.timeutils.decimal_relative_time
[timeutils.dt_to_timestamp]: http://boltons.readthedocs.org/en/latest/timeutils.html#boltons.timeutils.dt_to_timestamp
[timeutils.isoparse]: http://boltons.readthedocs.org/en/latest/timeutils.html#boltons.timeutils.isoparse
[timeutils.parse_timedelta]: http://boltons.readthedocs.org/en/latest/timeutils.html#boltons.timeutils.parse_timedelta
[timeutils.strpdate]: http://boltons.readthedocs.org/en/latest/timeutils.html#boltons.timeutils.strpdate
[typeutils.get_all_subclasses]: http://boltons.readthedocs.org/en/latest/typeutils.html#boltons.typeutils.get_all_subclasses
[typeutils.make_sentinel]: http://boltons.readthedocs.org/en/latest/typeutils.html#boltons.typeutils.make_sentinel
[urlutils]: http://boltons.readthedocs.org/en/latest/urlutils.html
[urlutils.SCHEME_PORT_MAP]: http://boltons.readthedocs.org/en/latest/urlutils.html#boltons.urlutils.SCHEME_PORT_MAP
[urlutils.find_all_links]: http://boltons.readthedocs.org/en/latest/urlutils.html#boltons.urlutils.find_all_links
