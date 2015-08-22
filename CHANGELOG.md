boltons Changelog
=================

Since February 20, 2013 there have been 13 releases and 615 commits for
an average of one 47-commit release every 2.5 months.

15.0.0
------
*(August 19, 2015)*

Finally the 15.0 major release. All passing PRs and feature requests
from the first wave addressed and closed. tzutils merged into
timeutils. AtomicSaver approach and API much improved. Several other
features added:

  * iterutils.backoff and iterutils.backoff_iter for exponential backoff
  * iterutils.frange and iterutils.xfrange for floating point range generation
  * Slightly more permissive jsonutils.JSONLIterator blank line ignoring
  * strutils.iter_splitlines for lazily getting lines from a larger string
  * timeutils.dt_to_timestamp, per the long-lived PR #13.
  * Merged tzutils into timeutils
  * fileutils.AtomicSaver rewrite and redoc
  * -teens support for strutils.ordinalize
  * made iterutils.one consistent with iterutils.first


0.6.6
-----
*(July 31, 2015)*

Fix atomic saving open-file issue for Windows.

  * Patch for AtomicSaver on Windows. Full rewrite comes in 15.0.0.
  * strutils.gunzip_bytes for decompressing a gzip bytestring


0.6.5
-----
*(July 30, 2015)*

BufferedSocket work, html2text, pairwise shortcut, is_container, plural
typo fix, timeutils.isoparse, cacheutils.ThresholdCounter, and lots of
testing

  * Add iterutils.first function
  * Add cacheutils.ThresholdCounter
  * Add JSONL verification to jsonutils
  * Add timeutils.isoparse
  * Add strutils.html2text and strutils.HTMLTextExtractor
  * Fix strutils.pluralize (indeces -> indices, per #41)
  * Add iterutils.is_container function
  * Fixed a small formatting bug in tbutils.ExceptionInfo that added
    an extra 'builtins.' for builtin exceptions under python 3
  * Added tests for many modules
  * Create iterutils.pairwise shortcuts for pairwise chunks since
    pairs (key/val) are common
  * Additional 2.6 compatibility and tests
  * Fixed CachedInstancePartial to be Python 3 friendly without breaking
    PyPy.
  * Made formatutils Python 3 compatible
  * Rename sockutils to socketutils and other changes


0.6.4
-----
*(May 10, 2015)*

Fixed multiline exception message handling in ParsedException. added
mathutils. adding a tentative version of socketutils. fix LRU.popitem. fix
OMD.__eq__.

  * Fix a bug where dictutils.OrderedMultiDict's __eq__ would fail
    with non-iterable objects of comparison
  * Fixed `LRU.popitem` to return a key value pair
  * Added mathutils with mathutils.ceil and mathutils.floor
    implementations that can search a fixed set of choices using the
    bisect module.
  * Fix excutils.ParsedException so exception message would not start
    with whitespace
  * Fix multiline exception messages
  * Adding socketutils.BufferedSocket and socketutils.NetstringSocket


0.6.3
-----
*(April 20, 2015)*

Add typeutils, remove compat.py, make ParsedException work with eval()ed
code

  * Properly parse tracebacks with missing source.  Resolves #30
  * Tweak the docs for typeutils.get_all_subclasses
  * Moved typeutils.make_sentinel into typeutils and removed the
    confusing compat module
  * Add in typeutils with modifications per the caveats of #15
  * Added function iterutils.one

0.6.2
-----
*(April 11, 2015)*

Add partial_ordering, fix LRU repr and addition behavior

  * Add funcutils.partial_ordering(), decorator similar to
    functools.total_ordering()
  * Fixed cacheutils.LRU's behavior per #21
  * Fix cacheutils.LRU repr reversal, fixes #20

0.6.0
-----
*(April 10, 2015)*

Python 3 support and several community bugfixes. Docs clarifications, too.

  * Make boltons Python 3 compatible without any external
    dependencies. All modules are independent and work in Python 2.6,
    2.7, 3.4, and PyPy.
  * clarify TracebackInfo.from_current() method gap, per user 'dl__'
    here: http://www.reddit.com/r/Python/comments/321d3o/boltons_over_100_python_utilities/
  * Fix the cacheutils.cached decorator, adding a sanity test, fixes #12
  * Fix bytes2human when builtin zip returns iterators
  * Simplified logic of iterutils.chunked

0.5.1
-----
*(April 10, 2015)*

A lot of bugfixes and Python 2.6 and PyPy compatibility changes thanks
to community contributions and encouragement.

  * Corrected cases where OMD was not exactly a dropin for OrderedDict
  * conditional availability of gcutils.get_all based on pypy or cpython, also
    gcutils.is_tracked was added in 2.7, so making gcutils.get_all work with 2.6
  * Made namedutils backwards compatibilty for python 2.6 best effort
  * Fix invalid part_path usage in fileutils.AtomicSaver

0.5.0
-----
*(April  9, 2015)*

First publicly released version. The major focus of this release was
docs, docstrings, and Read The Docs.

  * Cleared out __init__ module for maximum independence
  * making statsutils.median use _get_quantile and add statsutils.trimean
  * Switching the statsutils.Stats type to be more sorted-data oriented, since it's
    only for offline analysis of unordered data
  * Made consistent multi-line string formats, as well as usage of the
    term 'builtin' vs 'built-in' (noun vs adjective)
  * Instrumented LRI with stats tracking
  * Made timeutils.decimal_relative_time cardinalization optional
  * Removed timeutils dependency on strutils
  * Made tbutils.TracebackInfo classmethods work with no arguments.
  * Renamed ParsedTB to tbutils.ParsedException
  * Made dictutils.OMD .get()/.getlist() semantics more consistent.
  * finalizing .todict() and adding .sorted() to the dictutils.OMD
  * Removed osutils and adding a note about utils in general
  * Made cacheutils more consistent between LRU and LRI, adding some
    cacheutils docs
  * Deprecate osutils, moving its contents into fileutils
  * Adding in-process statsutils2, with new DataAnalyzer and
    get_pearson_type (not merged yet)


0.4.2
-----
*(March  8, 2015)*

Mostly a dictutils API update (addlist), but also gcutils.

  * dictutils.OMD: split out addlist() from add(), removing the multi
    kwarg
  * adding gcutils with gcutils.GCToggler and gc.get_all


0.4.1
-----
*(February 26, 2015)*

adding mboxutils

  * adding mboxutils for handy dandy /var/mail integrations like cronfed


0.4.0
-----
*(February 23, 2015)*

updated tbutils, JSONL support, initial cacheutils, atomic writer,
hashtags

  * tbutils: Changed the way exceptions are parsed out of tracebacks
  * tbutils: Guard against potential linecache issues
  * Defined/implemented iterutils.windowed_iter corner case behavior
  * Added from_path to fileutils.FilePerms
  * Adding strutils.find_hashtags
  * Add ignore patterns to fileutils.iter_find_files


0.3.0
-----
*(October 19, 2014)*

First alpha release. Practically, everything not mentioned above was
added in this release.

  * tbutils: add ContextualTracebackInfo and ContextualExceptionInfo
  * cacheutils: a few minor changes to the BasicCache
  * update tbutils with some critical bits. still need to add
    convenience method for ExceptionInfo -> default exception print,
    also need to add more docstrings.
  * adding initial jsonutils with JSONL support
  * added cacheutils.LRU
  * added timeutils.parse_timedelta
  * fixing iteritems with multi=False in the
    dictutils.OrderedMultiDict (should return first key, but last
    value not first)
  * debugutils: add pdb excepthook and debugutils.pdb_on_signal
  * add fileutils.mkdir_p
  * tableutils: add maxlen to table text stuff
  * fix date citation for gob's
  * adding pure-Python implementation of Gob's algorithm
  * fix object header guessing
  * namedutils: add namedtuple support
  * fix a headers bug in tableutils
  * tableutils: add a couple more do-not-recurse types, add
    UnsupportedData exception for better recursion, insert recursive
    entries in-line, improve 'Object' strategy heuristic
  * wrap up html tag customization and fix a related bug
  * make html configurable via class attributes
  * strengthen the max_depth check
  * InputType classes are just shorter and clearer, imo
  * new from_dict, from_list, from_object, removing old ones. almost
    used a MetaClass for this
  * starting new table
  * only update the integer for the field being updated
  * fixing a verbalization/pronunciation issue
  * no regex for better error messages
  * being opinionated about some FilePerms things
  * adding initial version of fileutils/FilePerms
  * update formatutils
  * fix a slightly nasty namedlist bug
  * make OrderedMultiDict.get()'s default allow singulars
  * sync over ExceptionInfo
  * add from_current() classmethod with depth option to Callpoint class
    for easier instantiation
  * it's called a numeronym
  * add a repr to ParsedTB. A bit verbose, but better than nothing.
  * add ParsedTB, which provides the ability to parse tracebacks dumped
    out to logs, the command line, etc.
  * improve test output and make assertion that new except hook is the
    same as the builtin.
  * update tbutils to use the more-powerful Callpoint type.
  * copy_function
  * partially clean up partial stuff
  * first version of the namedlist
  * fixing up namedtuple, groundwork for namedlist. humorously named
    module.
  * embed value in cell for incremental iteration boost on OMD
  * reorganize code, add 'default' argument to poplast()
  * make key argument optional to OMD.poplast
  * rectifying inconsistent names and adjusting respective tests
    accordingly. using smashcase because that's what builtin dict()
    uses.
  * fix reverse; missing yield from!
  * add initial table biz
  * add get_counts
  * add dictutils.OrderedMultiDict.get_inverted() for those handy reverse lookups
  * break out skip list to FastIter OMD + bench
  * add strutils.a10n()
  * fix a bug in dictutils.OrderedMultiDict's .add()
  * adding initial reimplementation of OMD
  * adding some tests to dictutils
  * update boltons formatutils to match what's goin on in lithoxyl
  * remove infer_pos_args() from strutils (already in formatutils)
  * add formatutils to boltons
  * fix a potential infinite recursion in LocalTZ
  * use more explicit names for Local/Constant tzinfo types
  * add a basic but handy file finder
  * add infer_positional_args() to strutils (from lithoxyl)
  * split BasicCache out of dictutils into cacheutils
  * update median calculation slightly
  * add appropriate stacklevel to deprutils warning
  * add an initial version of deprutils (basic utils for facilitating
    deprecation)
  * add bytes2human
  * first version of some basic timezone utils which came in handy for a
    train scheduling application I wrote (etavta)
  * reorder imports for pep8
  * redo plain-english relative_time() to have a decimal rounding factor
    and handle future dates
  * swap the order of cardinalize()'s arguments after intuiting the
    wrong order a couple times. gotta be consistent, this isn't PHP.
  * a weird little relative time approach
  * add total_seconds() implementation for Python <2.7, rename
    relative_datetime to relative_time
  * add a relative datetime function in a new module: timeutils
  * a little more transparency with orderedmultidict's maphistory
  * add a test for BasicCache
  * add the super simple BasicCache, a size-limited defaultdict-like
    thing
  * add a cheesy little splay list construct that can be used for splay-
    like manual reordering for eventual optimization
  * traceback utils, first draft
  * add strip_ansi() (need to make a cliutils or something)
  * add ansi strip task
  * mess with list tuning
  * add ordinalize()
  * add __all__ to statsutils
  * add more stats docs and doctests
  * add some stats functions
  * add unit_len()
  * add pluralize/singularize/cardinalize to strutils
  * add __all__s all around, clean up imports a bit
  * adding license
  * add sorted queue type, make it the default
  * fix little bug in insert
  * inheriting from list necessitates overriding the deprecated __get-,
    __set-, and __del- slice methods
  * hacky refactor to have a BasePriorityQueue to make room for
    SortedPriorityQueue with peek_n, etc.
  * add a little docstring and update sort method in BarrelList
  * add HeapPriorityQueue
  * tidy up listutils comments and imports
  * move treeutils out of boltons since I don't really think a pure
    python version actually adds much. i'll make an academic one-off
    repo for less practical data structure experiments like that.
  * inherit from list
  * add reverse() to blist
  * add index() to blist
  * cheesy __setitem__() for blist
  * add __delitem__() to BarrelList
  * change the way the in-place sort works with just one list
  * tune the list size a bit
  * add slicing to BarrelList
  * add initial version of BarrelList, a pure-python b-list-y thing to
    approximate O(log(n)) behavior by multiplexing the fast O(n) list
    operations
  * switch to new dead index interval approach; the IndexedSet is about
    half the speed of a list in the ultra-pathological case of random
    popping on the low end of the IndexedSet
  * made BisectTree's get() defaulting work a bit more like a dict's
  * added get_adjacent and miscellaneous to BisectTree
  * added a default name and always-falsy __nonzero__ to Sentinel
  * add pop() for BisectTree and export the generic Tree
  * make a bisect tree, because O(n) is still pretttttty fast up to
    about 100k items
  * add a little hack to chunked/chunked_iter to make it work nicely
    with strings
  * tidy up ki_vs_vi_lrh usage just a titch
  * revamp indices behavior (key_size and value_size)
  * switch to new multi-key mode
  * pretty much done porting insert, delete, balance (the basic
    operations)
  * switch to negative refs, arbitrary length nodes
  * add sentinel utility thing
  * add .index() for list compat, updated exception messages, and added
    a silly test to show off slicing and indexing
  * add slicing support and .clear()
  * remove ifilter dependency (using generator expression)
  * add .reverse and .sort() to IndexedSet, fix bisection related bug
    exposing MISSING (insort requested index, not real_index)
  * pretty much all fundy IndexedSet bugs hit and fixed, looks like
  * IndexedSet getting much closer
  * initial rough draft of IndexedSet with a short docstring and a bunch
    of fixes already (still not workin tho)
  * add dictutils (OrderedMultiDict)
  * it was a long time coming, but I'm finally halfway happy with this
    wrapped exception
  * add uniqueification capabilities
  * go back to using __new__ and positional arguments
  * exception wrapping green path mostly working
  * working on a wrapping exception mixin thing for less lossy
    nonraising.
  * add asciify and update slugify with ascii flag
  * add basic docs and doctests to strutils
  * scratch that, regexes still faster
  * add under2camel, camel2under, and slugify (and split_punct_ws, which
    is much faster than re-based punctuation splitting)
  * python3-compatible doctest for bucketize_bool
  * bucketize and bucketize_bool, with docs
  * add examples to chunked and chunked_iter
  * update split() docs with more examples.
  * iterutils.chunked_iter and iterutils.chunked
  * iterutils.split and iterutils.split_iter work
