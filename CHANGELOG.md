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
  * Fixed a small formatting bug in ExceptionInfo that added an extra
    'builtins.' for builtin exceptions under python 3
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

fixed multiline exception message handling in ParsedException. added
mathutils. adding a tentative version of sockutils. fix LRU.popitem. fix
OMD.__eq__.

  * fix a bug where __eq__ would fail with non-iterable objects of
    comparison
  * `LRU.popitem` should return a key value pair
  * Ignore Vim swap files
  * Correct typo in mathutils.ceil docstring.
  * Update function names in mathutils.rst.
  * refactoring ceil and floor to be simpler, more like stdlib. also
    modifying the respective tests. discussion on issue #36
  * shorter mathutils heading to make for a nicer TOC
  * update architecture statement after reflection on recent pull
    requests post-release
  * various docstring formatting tweaks for to mathutils
  * Ceil/floor function re-implementation using bisect. Corrections and
    updates to unittests and documentation.
  * Unittests for mathutils.py prepared for ceil/floor function re-
    implementation.
  * Minor edit to doctests in mathutils.py for readability (spacing
    between arguments).
  * Refactored ceil/floor function name and signature. Updated docs
    accordingly.
  * Add mathutils to index.rst.
  * New module for math utilities. Includes alternative ceiling/floor
    functions.
  * fixing last of sockutils test issues
  * think i got the rest of the bytes nonsense squared
  * sockutils: convert a vast majority of literals to explicit bytes
    literals (b'')
  * sockutils: switch all the print statements to print calls; compiling
    in python3.4
  * sockutils: fix an undefined variable, an unused variable, add an
    encoding line, and some minor formatting changes
  * Exception message should not start with whitespace
  * Fix multiline exception messages
  * Update sockutils.py
  * initial commit of BufferedSocket and NetstringSocket


0.6.3
-----
*(April 20, 2015)*

add typeutils, remove compat.py, make ParsedException work with eval()ed
code

  * a bit more robust for when tracebacks get cut off
  * Oops, broke last-line-eval-like tracebacks
  * Properly parse tracebacks with missing source.  Resolves #30
  * put a link to the PyPI in the README
  * tweak the docs for get_all_subclasses
  * add a note about the sentinel
  * moved make_sentinel into typeutils and deleted the confusing compat
    module
  * adding typeutils docs
  * fixing issubclass on pypy and making get_all_subclasses recurse
    properly and return a list
  * tweaks to issubclass
  * remove portions of typeutils as discussed in #15
  * classutils -> typeutils
  * windowed() -> windowed in index
  * read the docs has google analytics support built in!
  * adding a bit of the old (i,s,o,g,r,a,m) to the docs
  * enhance iterutils.one docs
  * classutils: Can't use set literals, sigh py2.6 compat
  * classutils.get_all_subclasses: Make doctest less fragile
  * classutils: python3 compat (fix print functions)
  * classutils: New module with utils based on classes, types and
    instances
  * defining __all__
  * added function one
  * updating the setup.py description
  * add python versions to index.rst
  * adding github stars to docs menu
  * add python versions to README
  * removing six dep in requirements-test.txt
  * trying out travis 2.6


0.6.2
-----
*(April 11, 2015)*

add partial_ordering, fix LRU repr and addition behavior

  * enhanced partial_ordering docs, added doctest from #19
  * fixes #21 - self.root was not being correctly updated, so the list
    never rotated out entries!
  * fix LRU repr reversal, fixes #20
  * funcutils: Add partial_ordering(), decorator similar to
    functools.total_ordering()


0.6.0
-----
*(April 10, 2015)*

Python 3 support and several community bugfixes. Docs clarification on
TracebackInfo

  * removing six.py install requirement
  * and python 3 support has landed
  * correcting tzutils.total_seconds doctest for different imports
    (should the doc be removed since it's a copy?)
  * basic Table python3 compat
  * tzutils independence from timeutils and relative import removal
  * independence and python 3 compat for setutils
  * removing the deprecated osutils
  * independent listutils + Python 3 support
  * independent iterutils + Python 3 support
  * gcutils Python 3 support
  * independent strutils, with Python 3 support
  * independent python3 compatibility for statsutils
  * independent namedutils Python 3 compat
  * funcutils independent Python 3 compat
  * independent fileutils Python 3 compat
  * clarify TracebackInfo.from_current() method gap, per user 'dl__'
    here: http://www.reddit.com/r/Python/comments/321d3o/boltons_over_10
    0_python_utilities/
  * quick fix to cached, adding a sanity test, fixes #12
  * .travis.yml: disable Python 2.6; enable 3.4
  * Python 3 support: add .compat.lrange; use with impunity
  * Python 3 support: .compat.xrange
  * Fix bytes2human when builtin zip returns iterators
  * Hack: don't use repr in asciify doctests
  * Python 3 support: integer division
  * Python 3 support: use f.__* instead of f.func_*
  * Hack: change a doctest to avoid repr(object) in Py3k
  * Python 3 support: use set operators to filter string contents
  * Python 3 support: types module
  * Python 3 support: use six.iteritems
  * Python 3 support: intra-package import
  * Use warnings.warn
  * Python 3 support: use six.string_types; fix map-as-list
  * Python 3 support: exec syntax
  * Python 3 support: exception handling syntax
  * Python 3 support: remove check in setup.py
  * Python 3 support: add six
  * Python 3 support: octal syntax
  * Python 3 support: print_function
  * dictutils passes on Python 3
  * iterutils Python 3 compat (izip/xrange)
  * cacheutils now python3 compatible
  * Fix reference to islice
  * Simplify logic of iterutils.chunked


0.5.1
-----
*(April 10, 2015)*

a lot of bugfixes and Python 2.6 and PyPy compatibility changes thanks
to community contributions and encouragement.

  * OMD not exactly a dropin for OrderedDict in many cases
  * adding pypy to travis and tox
  * tweaking the mro_items doctest to work on pypy and cpython
  * conditional availability of get_all based on pypy or cpython, also
    is_tracked was added in 2.7, so making get_all work with 2.6
  * wrap up a couple of float display issues so travis goes green for
    2.6
  * best-effort namedutils backwards compatibilty for python 2.6
  * adding initial .travis.yml, hold onto yr butts
  * adding initial tox.ini (just 2.7 for now)
  * fixing potential doctest failures due to dict key ordering
  * moving 'tests' directory out and under root as 'misc' (these are
    really more like utilities and examples)
  * Fix invalid part_path usage in fileutils
  * double the typos, double the fun
  * fix a link and update the docs nominal version (should automate
    this)
  * small fix to a doctest


0.5.0
-----
*(April  9, 2015)*

first real release version. Also, decked out with docs.

  * clear out __init__, as planned
  * make README highly linkful
  * tweak links in index.rst
  * tweaking index copy and adding proper linkage
  * minor update to date format
  * linking themes and adding architecture info blurb
  * Stats attr docstrings
  * making median use _get_quantile and add trimean
  * switching the Stats type to be more sorted-data oriented, since it's
    only for offline analysis of unordered data
  * index docs tweaks
  * hooray epilog replace. boltons now advertises its stats (might need
    to find a better place for them tho)
  * added the facilities necessary to automatically document how many
    modules, types, and functions there are in boltons.
  * splitting out the architecture into a separate document
  * add a note about online vs offline stats
  * adding some robust stats definitions and a bit of example code. made
    stats_helper take a default.
  * move new statsutils into place
  * rename DataAnalyzer to just plain Stats
  * couple of docstring fixes for tableutils
  * consistent multi-line string format and usage of the term 'builtin'
    vs 'built-in' (noun vs adjective)
  * cacheutils docs cleanup + add doctest for LRU
  * tableutils style consistency
  * strutils docs review and format style refresh
  * IndexedSet docs finalized (not perfect tho, thx autodoc you
    frustratin crap, no one said render the dunders)
  * setutils docs WIP
  * docs refresh for queueutils, including doctests
  * queueutils docs refresh and style changes
  * make the BList doctest a little tougher
  * listutils docs refresh + adding simple doctest
  * jsonutils docs tweaks (links, style changes)
  * iterutils refresh. argname change: keyfunc -> key. docs reviewed and
    updated.
  * gcutils docs refresh
  * funcutils doc refresh
  * formatutils docs refresh
  * fileutils docs complete
  * AtomicSaver docs refresh
  * dictutils docs reviewed and refreshed
  * fix all remaining modules' headings
  * debugutils docs refresh
  * documenting 'cached' decorator
  * more cacheutils docs tweaks (headings this time)
  * frozenset syntax. gotta run them tests before commit!
  * initial version of the cacheutils cached decorator
  * LRU repr fix
  * rearranging the cacheutils docs
  * LRI docstring tweak
  * cleaning up some unused code and instrumenting LRI with stats
  * cacheutils docs enhancements
  * wrapping back around to cacheutils docs work (and LRI enhancement)
  * tzutils docs and docstrings
  * made relative time cardinalization optional
  * remove timeutils dependency on strutils
  * timeutils docstrings
  * made TracebackInfo classmethods work with no arguments,
    documentation tweaks
  * renamed ParsedTB and tweak some docstrings and doc order
  * copy the list for the ParsedTB frames
  * tbutils docstrings 90% done
  * documenting tbutils
  * Table docstrings
  * some strutils docstring tweaks
  * fix AttributeErrors on doc generation
  * setutils docstrings
  * add docstrings for queueutils module
  * namedutils docs tweaks
  * tweaks in mboxutils docstrings
  * mboxutils docstrings
  * docstrings for listutils
  * plurals
  * try one more thing to get RTD's sphinx version to play nice with
    napoleon and themes
  * well that didn't fix it
  * now trying to fix RTD theme breakage
  * continuing to work around RTD sphinx version mess
  * napoleon/ReadTheDocs sphinx version fix
  * set a version requirement for sphinx
  * docstrings for the jsonutils module
  * Enable napoleon for docstrings.
  * also have tableutils use the sentinel factory (looks better in the
    docs)
  * have cacheutils use the sentinel factory (looks better in the docs)
  * minor whitespace
  * improve iterutils consistency, enhance docstrings and linking
  * adding gcutils docs and docstrings
  * adding funcutils docstrings, slight argument name tweak
  * adding formatutils docstrings
  * updating formatutils with defferedvalue
  * nvm, intersphinx glossary terms will have to wait
  * try something with the glossary
  * all major documentation changes for OMD complete. also made
    .get()/.getlist() semantics more consistent.
  * progress on intersphinxin
  * finalizing .todict() and adding .sorted() to the OMD
  * document all major public methods of dictutils.OrderedMultiDict and
    add an intro to the top.
  * add a little note to the top of debugutils
  * removing osutils and adding a note about utils in general
  * cacheutils inheritance docs
  * adding fileutils docs, including google-style docstring for
    AtomicSaver
  * LRU docs update
  * cacheutils doc updates
  * making cacheutils more consistent between LRU and LRI, adding some
    cacheutils docs
  * fix numbering
  * add notes about boltons usage
  * add a couple module docstrings
  * move osutils stuff into fileutils
  * updated headings for all the modules, thinking about merging osutils
    and fileutils
  * adding initial docs
  * statsutils2 is now ready to take the place of statsutils, with
    backwards-compatible global convenience functions, etc.
  * adding in-process statsutils2, with new DataAnalyzer and
    get_pearson_type (not merged yet)


0.4.2
-----
*(March  8, 2015)*

dictutils API update (addlist)

  * add gc.get_all() for getting all instances of a type, update TODO
  * minro OMD API change: split out addlist() from add(), removing the
    multi kwarg
  * add gcutils test and comment; update TODO
  * adding GCToggler/gcutils


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

  * add a couple files to the tests directory
  * change the way exceptions are parsed out of tracebacks
  * raw string for regex pattern, rephrase comment
  * guard against linecache non-safety
  * defined/implemented windowed_iter corner case behavior
  * working on windowed_iter
  * refactor atomic_save to put more into the context manager. works
    like a charm.
  * in progress commit of success_swap (name definitely going to
    change), also add from_path to FilePerms
  * adding find_hashtags to strutils
  * add ignore patterns to osutils.iter_find_files


0.3.0
-----
*(October 19, 2014)*

add a ton of stuff, tbutils, namedlist, and much more

  * add Contextual* to tbutils, clarify APIs a bit
  * a few minor changes to the BasicCache
  * update tbutils with some critical bits. still need to add
    convenience method for ExceptionInfo -> default exception print,
    also need to add more docstrings.
  * add some temporary test files and remove some cruft
  * adding initial jsonutils with JSONL support
  * LRU pretty much complete. needs more testing, obviously.
  * workin on the LRU
  * LRU in progress
  * fix .keys -> .keys()
  * add a small but robust relative time parser
  * fixing iteritems with multi=False in the OMD (should return first
    key, but last value not first)
  * fix an error message
  * add pdb excepthook and some helpful docstrings
  * fix pdb_on_signal, add a helpful comment
  * mkdir -p
  * add maxlen to table text stuff (not finalized)
  * my most commonly used signal handler, great for getting at anything
    that has an infinite loop (intentional or not)
  * fix date citation for gob's
  * fixing string formatting issues in implementation of gob (2013)
  * adding pure-Python implementation of Gob's algorithm
  * fix object header guessing
  * Updating tableutils:
  * add namedtuple support and update a couple notes
  * fix a headers bug in tableutils
  * tableutils: add a couple more do-not-recurse types, add
    UnsupportedData exception for better recursion, insert recursive
    entries in-line, improve 'Object' strategy heuristic
  * add a little note
  * wrap up html tag customization and fix a related bug
  * make html configurable via class attributes
  * strengthen the max_depth check
  * InputType classes are just shorter and clearer, imo
  * new from_dict, from_list, from_object, removing old ones. almost
    used a MetaClass for this
  * rearrange some table code
  * recursive HTML output achieved
  * huge amount of Table work, but most prominently, got abstract and
    recursive loading initially working
  * adding a couple more notes
  * tweaking Table text output and adding notes and TODOs
  * add from_object()
  * html escaping
  * adding text formatting
  * html fixes and vertical tables
  * to_html
  * making good progress on the list-backed table
  * starting new table
  * only update the integer for the field being updated
  * fixing a verbalization/pronunciation issue
  * no regex for better error messages
  * being opinionated about some FilePerms things
  * adding initial version of fileutils/FilePerms
  * update formatutils
  * fix a slightly nasty namedlist bug
  * make OrderedMultiDict.get()'s default allow singulars
  * "level" is a better argname than "depth"
  * sync over ExceptionInfo
  * add from_current() classmethod with depth option to Callpoint class
    for easier instantiation
  * it's called a numeronym
  * add a repr to ParsedTB. A bit verbose, but better than nothing.
  * add ParsedTB, which provides the ability to parse tracebacks dumped
    out to logs, the command line, etc.
  * improve test output and make assertion that new except hook is the
    same as the builtin.
  * fixed potential issue with from_traceback, test improvements in
    progress
  * update tbutils to use the more-powerful Callpoint type.
  * copy_function
  * partially clean up partial stuff
  * first version of the namedlist
  * fixing up namedtuple, groundwork for namedlist. humorously named
    module.
  * adding consistency
  * minor tweak to OMD benchscript
  * remove duplicated add() logic in FIOMD
  * now that vals are embedded in the LL, remove duplicated setitem in
    FIOMD
  * remove some leftover @profiles
  * embed value in cell for incremental iteration boost on OMD
  * add multi=True bench functionality
  * remove duplicated topmatter.
  * fix __reversed__ for realz
  * reorganize code, add 'default' argument to poplast()
  * make key argument optional to OMD.poplast
  * rectifying inconsistent names and adjusting respective tests
    accordingly. using smashcase because that's what builtin dict()
    uses.
  * fix reverse; missing yield from!
  * slightly clearer doc string
  * add initial table biz
  * fix a smidge of whitespace
  * add get_counts
  * fix a typo in _bench_omd
  * add get_inverted() for those handy reverse lookups
  * retain ugly super calls, since we don't want OMD's help
  * fix super calls from fast refactor :(
  * break out skip list to FastIter OMD + bench
  * better _remove{,_all} code, should be correct
  * reversed fixed
  * values inside skip list
  * first draft skip list
  * add some more update* tests
  * speed up iterkeys by removing one layer of generator on multi=False
  * add a10n()
  * enhance OMD bench script
  * fix itervalues
  * add the 'multi' dimension to strictly_ascending
  * fix a bug in .add()
  * add 'kv consistency' test (currenty failing, see note in .values())
  * add 'strictly ascending' test
  * various bug fixing, noting, and cleanup
  * fix a typo in OMD.keys()
  * more iteration optimization
  * switch OMD benching to use lithoxyl for stats, etc., and compare
    against other mapping implementations
  * a few more optimizations (around iteration this time)
  * actually test different implementations
  * an assortment of minor optimizations to dictutils
  * tweak for side-by-side benchin
  * temporarily add the bencher why not
  * add some notes/doctests
  * add get_flattened, etc.
  * add clear tests
  * fix get() (always return copies of lists, so as not to blow up the
    mutable state.)
  * add some tweaks, notes, TODOs (and doctest bits)
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
  * add note about quiet deprecation warnings
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
  * add a couple tests for the SplayList
  * add a cheesy little splay list construct that can be used for splay-
    like manual reordering for eventual optimization
  * TODO: fix linecache
  * traceback utils, first draft
  * add strip_ansi() (need to make a cliutils or something)
  * add ansi strip task
  * mess with list tuning
  * add ordinalize()
  * expose stats functions at the package level
  * add __all__ to statsutils
  * add more stats docs and doctests
  * add some stats functions and notes
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
  * tweak slicing and add sort() to barrel list
  * add slicing to BarrelList
  * add some notes on IndexedSet
  * add initial version of BarrelList, a pure-python b-list-y thing to
    approximate O(log(n)) behavior by multiplexing the fast O(n) list
    operations
  * hm, wording
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
  * fix a couple minor bugs
  * cleaned up a bit more even
  * more test work, make insert_many work
  * more code restructuring and cleanup
  * tidy up ki_vs_vi_lrh usage just a titch
  * revamp indices behavior (key_size and value_size)
  * mostly cleaned up
  * all tests passing, time to clean up
  * closed the deal
  * so very close
  * gettin real close
  * tmp commit, workin on delete
  * tested the multi-key mode and tweaked a bit here and there
  * switch to new multi-key mode
  * pretty much done porting insert, delete, balance (the basic
    operations)
  * switch to negative refs, arbitrary length nodes, clean up tree tests
  * passing the gauntlet
  * even more progress
  * even more progress
  * more progress
  * more progress
  * coming along
  * tweaking the treeeee
  * add initial version of balancing tree
  * add sentinel utility thing
  * temp patch for bug in getitem()
  * temp patch for bug in pop()
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
  * a bit of packaging
  * it was a long time coming, but I'm finally halfway happy with this
    wrapped exception
  * docs tweak on unique_iter
  * add uniqueification capabilities
  * go back to using __new__ and positional arguments
  * add a note and tweak some output code
  * add some docs
  * exception wrapping green path mostly working
  * working on a wrapping exception mixin thing for less lossy
    nonraising.
  * a note on StringBuffer
  * progress on the string buffer
  * add note and attribution
  * add asciify and update slugify with ascii flag
  * add basic docs and doctests to strutils
  * scratch that, regexes still faster
  * add under2camel, camel2under, and slugify (and split_punct_ws, which
    is much faster than re-based punctuation splitting)
  * python3-compatible doctest for bucketize_bool
  * a couple iterutils changes
  * bucketize and bucketize_bool, with docs
  * add examples to chunked and chunked_iter
  * update split() docs with more examples.
  * chunked_iter and chunked
  * (nest directory)
  * split and split_iter work
