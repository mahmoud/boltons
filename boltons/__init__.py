"""
mkinit ~/code/boltons/boltons/__init__.py
"""
# flake8: noqa

import os

__version__ = '19.3.1dev'


def enable_flatapi():
    from boltons.cacheutils import (CachedFunction, CachedMethod, DEFAULT_MAX_SIZE,
                                    LRI, LRU, MinIDMap, ThresholdCounter, cached,
                                    cachedmethod, cachedproperty, make_cache_key,)
    from boltons.cmdutils import (cmd,)
    from boltons.debugutils import (pdb_on_exception, pdb_on_signal, wrap_trace,)
    from boltons.deprutils import (DeprecatableModule, ModuleType,
                                   deprecate_module_member,)
    from boltons.dictutils import (FrozenDict, ManyToMany, MultiDict, OMD,
                                   OneToOne, OrderedMultiDict, subdict,)
    from boltons.easterutils import (gobs_program,)
    from boltons.ecoutils import (CPU_COUNT, ECO_VERSION, EXPAT_VERSION, HAVE_IPV6,
                                  HAVE_READLINE, HAVE_THREADING, HAVE_UCS4,
                                  HAVE_URANDOM, INSTANCE_ID, IS_64BIT,
                                  OPENSSL_VERSION, PY_GT_2, SQLITE_VERSION,
                                  START_TIME_INFO, TKINTER_VERSION, ZLIB_VERSION,
                                  get_profile, get_profile_json, get_python_info,
                                  getrandbits, main,)
    from boltons.excutils import (ExceptionCauseMixin,)
    from boltons.fileutils import (AtomicSaver, FilePerms, atomic_save, copytree,
                                   iter_find_files, mkdir_p,)
    from boltons.formatutils import (BaseFormatField, DeferredValue,
                                     construct_format_field_str, get_format_args,
                                     infer_positional_format_args,
                                     tokenize_format_str,)
    from boltons.funcutils import (CachedInstancePartial, ExistingArgument,
                                   FunctionBuilder, InstancePartial,
                                   MissingArgument, NO_DEFAULT, copy_function,
                                   dir_dict, format_exp_repr, format_invocation,
                                   format_nonexp_repr, get_module_callables,
                                   make_method, mro_items, partial,
                                   partial_ordering, wraps,)
    from boltons.gcutils import (GCToggler, get_all, toggle_gc,
                                 toggle_gc_postcollect,)
    from boltons.ioutils import (MultiFileReader, READ_CHUNK_SIZE, SpooledBytesIO,
                                 SpooledIOBase, SpooledStringIO, binary_type,
                                 is_text_fileobj, text_type,)
    from boltons.iterutils import (GUIDerator, PathAccessError,
                                   SequentialGUIDerator, backoff, backoff_iter,
                                   bucketize, chunked, chunked_iter, default_enter,
                                   default_exit, default_visit, first, flatten,
                                   flatten_iter, frange, get_path, guid_iter,
                                   is_collection, is_iterable, is_scalar, one,
                                   pairwise, pairwise_iter, partition, redundant,
                                   remap, research, same, seq_guid_iter,
                                   soft_sorted, split, split_iter, unique,
                                   unique_iter, windowed, windowed_iter, xfrange,)
    from boltons.jsonutils import (JSONLIterator, reverse_iter_lines,)
    from boltons.listutils import (BList, BarrelList,)
    from boltons.mathutils import (Bits, ceil, clamp, floor,)
    from boltons.mboxutils import (DEFAULT_MAXMEM, mbox_readonlydir,)
    from boltons.namedutils import (namedlist, namedtuple,)
    from boltons.queueutils import (BasePriorityQueue, HeapPriorityQueue,
                                    PriorityQueue, SortedPriorityQueue,)
    from boltons.setutils import (IndexedSet, complement,)
    from boltons.socketutils import (BufferedSocket, ConnectionClosed,
                                     DEFAULT_MAXSIZE, DEFAULT_TIMEOUT, Error,
                                     MessageTooLong, NetstringInvalidSize,
                                     NetstringMessageTooLong,
                                     NetstringProtocolError, NetstringSocket,
                                     Timeout,)
    from boltons.statsutils import (Stats, describe, format_histogram_counts,)
    from boltons.strutils import (a10n, args2cmd, args2sh, asciify, bytes2human,
                                  camel2under, cardinalize, escape_shell_args,
                                  find_hashtags, format_int_list, gunzip_bytes,
                                  gzip_bytes, html2text, indent, is_ascii, is_uuid,
                                  iter_splitlines, ordinalize, parse_int_list,
                                  pluralize, singularize, slugify, split_punct_ws,
                                  strip_ansi, under2camel, unit_len,)
    from boltons.tableutils import (Table,)
    from boltons.tbutils import (Callpoint, ContextualCallpoint,
                                 ContextualExceptionInfo, ContextualTracebackInfo,
                                 ExceptionInfo, ParsedException, TracebackInfo,
                                 print_exception,)
    from boltons.timeutils import (Central, ConstantTZInfo, DSTEND_1967_1986,
                                   DSTEND_1987_2006, DSTEND_2007,
                                   DSTSTART_1967_1986, DSTSTART_1987_2006,
                                   DSTSTART_2007, EPOCH_AWARE, EPOCH_NAIVE,
                                   Eastern, HOUR, LocalTZ, LocalTZInfo, Mountain,
                                   Pacific, USTimeZone, UTC, ZERO, daterange,
                                   decimal_relative_time, dt_to_timestamp,
                                   isoparse, parse_td, parse_timedelta,
                                   relative_time, strpdate, total_seconds,)
    from boltons.typeutils import (classproperty, get_all_subclasses,
                                   make_sentinel,)
    from boltons.urlutils import (DEFAULT_ENCODING, DEFAULT_PARSED_URL,
                                  NO_NETLOC_SCHEMES, OMD, OrderedMultiDict,
                                  QueryParamDict, SCHEME_PORT_MAP, URL,
                                  URLParseError, cachedproperty, find_all_links,
                                  parse_host, parse_qsl, parse_url,
                                  quote_fragment_part, quote_path_part,
                                  quote_query_part, quote_userinfo_part,
                                  register_scheme, resolve_path_parts, to_unicode,
                                  unicode, unquote, unquote_to_bytes,)
    # EVERYTHING IS TOP LEVEL NOW
    globals().update(**locals())


import os
FLATMODE = (os.environ.get('BOLTONS_FLATMODE', '') == 'TRUE')

if FLATMODE:
    enable_flatapi()
