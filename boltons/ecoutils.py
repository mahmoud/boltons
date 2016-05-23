# -*- coding: utf-8 -*-
"""The goal of the survey is to provide an information-dense
description of critical runtime factors while minimizing side
effects. The expected execution time for collection and uploading the
description is 100ms or less. This depends on the network speed to the
datastore, but as of writing, the execution time to localhost is
80ms. The message is designed to fit in one path MTU, and is currently
at around 1000 bytes of JSON in normal cases, but this can grow with
the sizes of paths

# Notable omissions

Due to space constraints (and possibly latency constraints), the
following information is deemed not dense enough, and thus omitted:

* sys.path
* full sysconfig
* environment variables
  *

# Compatibility

So far ecoutils has has been tested on Python 2.6, 2.7, 3.4, 3.5, and
PyPy.
"""

import re
import os
import sys
import json
import time
import uuid
import socket
import getpass
import datetime
import platform

ECO_VERSION = '1.0.0'

PY_GT_2 = sys.version_info[0] > 2

INSTANCE_ID = uuid.uuid4()
IS_64BIT = sys.maxsize > 2 ** 32
HAVE_UCS4 = getattr(sys, 'maxunicode', 0) > 65536
HAVE_READLINE = True

try:
    import readline
except Exception:
    HAVE_READLINE = False

try:
    import sqlite3
    SQLITE_VERSION = sqlite3.sqlite_version
except Exception:
    SQLITE_VERSION = ''


try:

    import ssl
    try:
        OPENSSL_VERSION = ssl.OPENSSL_VERSION
    except AttributeError:
        # This is a conservative estimate for Python <2.6
        # SSL module added in 2006, when 0.9.7 was standard
        OPENSSL_VERSION = 'OpenSSL >0.8.0'
except Exception:
    OPENSSL_VERSION = ''


try:
    if PY_GT_2:
        import tkinter
    else:
        import Tkinter as tkinter
    TKINTER_VERSION = str(tkinter.TkVersion)
except Exception:
    TKINTER_VERSION = ''


try:
    import zlib
    ZLIB_VERSION = zlib.ZLIB_VERSION
except Exception:
    ZLIB_VERSION = ''


try:
    from xml.parsers import expat
    EXPAT_VERSION = expat.EXPAT_VERSION
except Exception:
    EXPAT_VERSION = ''


try:
    from multiprocessing import cpu_count
    CPU_COUNT = cpu_count()
except:
    CPU_COUNT = None

# TODO: have_ipv6

try:
    import threading
    HAVE_THREADING = True
except Exception:
    HAVE_THREADING = False


try:
    HAVE_IPV6 = socket.has_ipv6
except Exception:
    HAVE_IPV6 = False


try:
    from resource import getrlimit, RLIMIT_NOFILE
    RLIMIT_FDS_SOFT, RLIMIT_FDS_HARD = getrlimit(RLIMIT_NOFILE)
except Exception:
    RLIMIT_FDS_SOFT, RLIMIT_FDS_HARD = 0, 0


START_TIME_INFO = {'time_utc': str(datetime.datetime.utcnow()),
                   'time_utc_offset': -time.timezone / 3600.0}


def get_python_info():
    ret = {}
    ret['argv'] = _escape_shell_args(sys.argv)
    ret['bin'] = sys.executable

    # Even though compiler/build_date are already here, they're
    # actually parsed from the version string. So, in the rare case of
    # the unparsable version string, we're still transmitting it.
    ret['version'] = sys.version

    ret['compiler'] = platform.python_compiler()
    ret['build_date'] = platform.python_build()[1]
    ret['version_info'] = list(sys.version_info)

    ret['features'] = {'openssl': OPENSSL_VERSION,
                       'expat': EXPAT_VERSION,
                       'sqlite': SQLITE_VERSION,
                       'tkinter': TKINTER_VERSION,
                       'zlib': ZLIB_VERSION,
                       'unicode_wide': HAVE_UCS4,
                       'readline': HAVE_READLINE,
                       '64bit': IS_64BIT,
                       'ipv6': HAVE_IPV6,
                       'threading': HAVE_THREADING}

    return ret


def get_profile():
    ret = {}
    ret['username'] = getpass.getuser()
    ret['uuid'] = str(INSTANCE_ID)
    ret['hostname'] = socket.gethostname()
    ret['hostfqdn'] = socket.getfqdn()
    uname = platform.uname()
    ret['uname'] = {'system': uname[0],
                    'node': uname[1],
                    'release': uname[2],  # linux: distro name
                    'version': uname[3],  # linux: kernel version
                    'machine': uname[4],
                    'processor': uname[5]}
    linux_dist = platform.linux_distribution()
    ret['linux_dist_name'] = linux_dist[0]
    ret['linux_dist_version'] = linux_dist[1]
    ret['cpu_count'] = CPU_COUNT

    ret['fs_encoding'] = sys.getfilesystemencoding()
    ret['ulimit_soft'] = RLIMIT_FDS_SOFT
    ret['ulimit_hard'] = RLIMIT_FDS_HARD
    ret['cwd'] = os.getcwd()
    ret['umask'] = '{0:03o}'.format(os.umask(os.umask(2)))

    ret['python'] = get_python_info()
    ret.update(START_TIME_INFO)
    ret['_eco_version'] = ECO_VERSION
    return ret


def main():
    data_dict = get_profile()
    print(json.dumps(data_dict, sort_keys=True, indent=2))

    return

#############################################
#  The shell escaping copied in from strutils
#############################################


def _escape_shell_args(args, sep=' ', style=None):
    if not style:
        style = 'cmd' if sys.platform == 'win32' else 'sh'

    if style == 'sh':
        return _args2sh(args, sep=sep)
    elif style == 'cmd':
        return _args2cmd(args, sep=sep)

    raise ValueError("style expected one of 'cmd' or 'sh', not %r" % style)


_find_sh_unsafe = re.compile(r'[^a-zA-Z0-9_@%+=:,./-]').search


def _args2sh(args, sep=' '):
    # see strutils
    ret_list = []

    for arg in args:
        if not arg:
            ret_list.append("''")
            continue
        if _find_sh_unsafe(arg) is None:
            ret_list.append(arg)
            continue
        # use single quotes, and put single quotes into double quotes
        # the string $'b is then quoted as '$'"'"'b'
        ret_list.append("'" + arg.replace("'", "'\"'\"'") + "'")

    return ' '.join(ret_list)


def _args2cmd(args, sep=' '):
    # see strutils
    result = []
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


############################
#  End shell escaping code
############################

if __name__ == '__main__':
    main()
