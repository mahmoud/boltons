# -*- coding: utf-8 -*-
"""

xdoctest -m netharn.export.closer _closefile --fpath=$HOME/code/boltons/tests/test_cmdutils.py --modnames=ubelt,

"""
import pytest
import sys
import io
import six
from os.path import join
from os.path import expanduser
from os.path import normpath
import os
from boltons.cmdutils import cmd


WIN32 = (sys.platform == 'win32')
LINUX = sys.platform.startswith('linux')
DARWIN = (sys.platform == 'darwin')


def platform_cache_dir():
    """
    Returns a directory which should be writable for any application
    This should be used for temporary deletable data.

    Returns:
        str : path to the cache dir used by the current operating system
    """
    if LINUX:  # nocover
        dpath_ = os.environ.get('XDG_CACHE_HOME', '~/.cache')
    elif DARWIN:  # nocover
        dpath_  = '~/Library/Caches'
    elif WIN32:  # nocover
        dpath_ = os.environ.get('LOCALAPPDATA', '~/AppData/Local')
    else:  # nocover
        raise NotImplementedError('Unknown Platform  %r' % (sys.platform,))
    dpath = normpath(expanduser(dpath_))
    return dpath


def get_app_cache_dir(appname, *args):
    r"""
    Returns a writable directory for an application.
    This should be used for temporary deletable data.

    Args:
        appname (str): the name of the application
        *args: any other subdirectories may be specified

    Returns:
        str : dpath: writable cache directory for this application

    SeeAlso:
        ensure_app_cache_dir
    """
    dpath = join(platform_cache_dir(), appname, *args)
    return dpath


def ensure_app_cache_dir(appname, *args):
    """
    Calls :func:`get_app_cache_dir` but ensures the directory exists.

    Args:
        appname (str): the name of the application
        *args: any other subdirectories may be specified

    SeeAlso:
        get_app_cache_dir

    Example:
        >>> dpath = ensure_app_cache_dir('boltons')
        >>> assert exists(dpath)
    """
    dpath = get_app_cache_dir(appname, *args)
    from boltons import fileutils
    fileutils.mkdir_p(dpath)
    return dpath


def ensure_app_resource_dir(appname, *args):  # nocover
    """
    Calls `get_app_resource_dir` but ensures the directory exists.

    DEPRICATED in favor of ensure_app_config_dir / ensure_app_data_dir

    Args:
        appname (str): the name of the application
        *args: any other subdirectories may be specified

    SeeAlso:
        get_app_resource_dir
    """
    return ensure_app_cache_dir(appname, *args)


def codeblock(block_str):
    """
    Create a block of text that preserves all newlines and relative indentation

    Wraps multiline string blocks and returns unindented code.
    Useful for templated code defined in indented parts of code.

    Args:
        block_str (str): typically in the form of a multiline string

    Returns:
        str: the unindented string

    Example:
        >>> # Simulate an indented part of code
        >>> if True:
        >>>     # notice the indentation on this will be normal
        >>>     codeblock_version = codeblock(
        ...             '''
        ...             def foo():
        ...                 return 'bar'
        ...             '''
        ...         )
        >>>     # notice the indentation and newlines on this will be odd
        >>>     normal_version = ('''
        ...         def foo():
        ...             return 'bar'
        ...     ''')
        >>> assert normal_version != codeblock_version
        >>> print('Without codeblock')
        >>> print(normal_version)
        >>> print('With codeblock')
        >>> print(codeblock_version)
    """
    import textwrap  # this is a slow import, do it lazy
    return textwrap.dedent(block_str).strip('\n')


class TeeStringIO(io.StringIO):
    """
    An IO object that writes to itself and another IO stream.

    Attributes:
        redirect (io.IOBase): The other stream to write to.

    Example:
        >>> redirect = io.StringIO()
        >>> self = TeeStringIO(redirect)
    """
    def __init__(self, redirect=None):
        self.redirect = redirect
        super(TeeStringIO, self).__init__()

    def isatty(self):  # nocover
        """
        Returns true of the redirect is a terminal.

        Notes:
            Needed for IPython.embed to work properly when this class is used
            to override stdout / stderr.
        """
        return (self.redirect is not None and
                hasattr(self.redirect, 'isatty') and self.redirect.isatty())

    @property
    def encoding(self):
        """
        Gets the encoding of the `redirect` IO object

        Example:
            >>> redirect = io.StringIO()
            >>> assert TeeStringIO(redirect).encoding is None
            >>> assert TeeStringIO(None).encoding is None
            >>> assert TeeStringIO(sys.stdout).encoding is sys.stdout.encoding
            >>> redirect = io.TextIOWrapper(io.StringIO())
            >>> assert TeeStringIO(redirect).encoding is redirect.encoding
        """
        if self.redirect is not None:
            return self.redirect.encoding
        else:
            return super(TeeStringIO, self).encoding

    def write(self, msg):
        """
        Write to this and the redirected stream
        """
        if self.redirect is not None:
            self.redirect.write(msg)
        if six.PY2:
            from xdoctest.utils.util_str import ensure_unicode
            msg = ensure_unicode(msg)
        super(TeeStringIO, self).write(msg)

    def flush(self):  # nocover
        """
        Flush to this and the redirected stream
        """
        if self.redirect is not None:
            self.redirect.flush()
        super(TeeStringIO, self).flush()


class CaptureStream(object):
    """
    Generic class for capturing streaming output from stdout or stderr
    """


class CaptureStdout(CaptureStream):
    r"""
    Context manager that captures stdout and stores it in an internal stream

    Args:
        supress (bool, default=True):
            if True, stdout is not printed while captured
        enabled (bool, default=True):
            does nothing if this is False

    Example:
        >>> self = CaptureStdout(supress=True)
        >>> print('dont capture the table flip (╯°□°）╯︵ ┻━┻')
        >>> with self:
        ...     text = 'capture the heart ♥'
        ...     print(text)
        >>> print('dont capture look of disapproval ಠ_ಠ')
        >>> assert isinstance(self.text, six.text_type)
        >>> assert self.text == text + '\n', 'failed capture text'

    Example:
        >>> self = CaptureStdout(supress=False)
        >>> with self:
        ...     print('I am captured and printed in stdout')
        >>> assert self.text.strip() == 'I am captured and printed in stdout'

    Example:
        >>> self = CaptureStdout(supress=True, enabled=False)
        >>> with self:
        ...     print('dont capture')
        >>> assert self.text is None
    """
    def __init__(self, supress=True, enabled=True):
        self.enabled = enabled
        self.supress = supress
        self.orig_stdout = sys.stdout
        if supress:
            redirect = None
        else:
            redirect = self.orig_stdout
        self.cap_stdout = TeeStringIO(redirect)
        self.text = None

        self._pos = 0  # keep track of how much has been logged
        self.parts = []
        self.started = False

    def log_part(self):
        """ Log what has been captured so far """
        self.cap_stdout.seek(self._pos)
        text = self.cap_stdout.read()
        self._pos = self.cap_stdout.tell()
        self.parts.append(text)
        self.text = text

    def start(self):
        if self.enabled:
            self.text = ''
            self.started = True
            sys.stdout = self.cap_stdout

    def stop(self):
        """
        Example:
            >>> CaptureStdout(enabled=False).stop()
            >>> CaptureStdout(enabled=True).stop()
        """
        if self.enabled:
            self.started = False
            sys.stdout = self.orig_stdout

    def __enter__(self):
        self.start()
        return self

    def __del__(self):  # nocover
        if self.started:
            self.stop()
        if self.cap_stdout is not None:
            self.close()

    def close(self):
        self.cap_stdout.close()
        self.cap_stdout = None

    def __exit__(self, type_, value, trace):
        if self.enabled:
            try:
                self.log_part()
            except Exception:  # nocover
                raise
            finally:
                self.stop()
        if trace is not None:
            return False  # return a falsey value on error


def test_cmd_stdout():
    with CaptureStdout() as cap:
        result = cmd('echo hello stdout', verbose=True)
    assert result['out'].strip() == 'hello stdout'
    assert cap.text.strip() == 'hello stdout'


def test_cmd_veryverbose():
    with CaptureStdout() as cap:
        result = cmd('echo hello stdout', verbose=3)
    assert result['out'].strip() == 'hello stdout'
    print(cap.text)
    # assert cap.text.strip() == 'hello stdout'


def test_tee_false():
    with CaptureStdout() as cap:
        result = cmd('echo hello stdout', verbose=3, tee=False)
    assert result['out'].strip() == 'hello stdout'
    assert 'hello world' not in cap.text
    print(cap.text)


def test_cmd_stdout_quiet():
    with CaptureStdout() as cap:
        result = cmd('echo hello stdout', verbose=False)
    assert result['out'].strip() == 'hello stdout', 'should still capture internally'
    assert cap.text.strip() == '', 'nothing should print to stdout'


def test_cmd_stderr():
    result = cmd('echo hello stderr 1>&2', shell=True, verbose=True)
    assert result['err'].strip() == 'hello stderr'


def test_cmd_tee_auto():
    command = 'python -c "for i in range(100): print(str(i))"'
    result = cmd(command, verbose=0, tee_backend='auto')
    assert result['out'] == '\n'.join(list(map(str, range(100)))) + '\n'


def test_cmd_tee_thread():
    if 'tqdm' in sys.modules:
        if tuple(map(int, sys.modules['tqdm'].__version__.split('.'))) < (4, 19):
            pytest.skip(reason='threads cause issues with early tqdms')

    import threading
    # check which threads currently exist (ideally 1)
    existing_threads = list(threading.enumerate())
    print('existing_threads = {!r}'.format(existing_threads))

    command = 'python -c "for i in range(10): print(str(i))"'
    result = cmd(command, verbose=0, tee_backend='thread')
    assert result['out'] == '\n'.join(list(map(str, range(10)))) + '\n'

    after_threads = list(threading.enumerate())
    print('after_threads = {!r}'.format(after_threads))
    assert len(existing_threads) <= len(after_threads), (
        'we should be cleaning up our threads')


@pytest.mark.skipif(sys.platform == 'win32', reason='not available on win32')
def test_cmd_tee_select():
    command = 'python -c "for i in range(100): print(str(i))"'
    result = cmd(command, verbose=1, tee_backend='select')
    assert result['out'] == '\n'.join(list(map(str, range(100)))) + '\n'

    command = 'python -c "for i in range(100): print(str(i))"'
    result = cmd(command, verbose=0, tee_backend='select')
    assert result['out'] == '\n'.join(list(map(str, range(100)))) + '\n'


@pytest.mark.skipif(sys.platform == 'win32', reason='not available on win32')
def test_cmd_tee_badmethod():
    command = 'python -c "for i in range(100): print(str(i))"'
    with pytest.raises(ValueError):
        cmd(command, verbose=2, tee_backend='bad tee backend')


def test_cmd_multiline_stdout():
    command = 'python -c "for i in range(10): print(str(i))"'
    result = cmd(command, verbose=0)
    assert result['out'] == '\n'.join(list(map(str, range(10)))) + '\n'


@pytest.mark.skipif(sys.platform == 'win32', reason='does not run on win32')
def test_cmd_interleaved_streams_sh():
    """
    A test that ``Crosses the Streams'' of stdout and stderr

    pytest tests/test_cmd.py::test_cmd_interleaved_streams_sh
    """
    if False:
        sh_script = codeblock(
            r'''
            for i in `seq 0 29`;
            do
                sleep .001
                >&1 echo "O$i"
                if [ "$(($i % 5))" = "0" ]; then
                    >&2 echo "!E$i"
                fi
            done
            ''').lstrip()
        result = cmd(sh_script, shell=True, verbose=0)

        assert result['out'] == 'O0\nO1\nO2\nO3\nO4\nO5\nO6\nO7\nO8\nO9\nO10\nO11\nO12\nO13\nO14\nO15\nO16\nO17\nO18\nO19\nO20\nO21\nO22\nO23\nO24\nO25\nO26\nO27\nO28\nO29\n'
        assert result['err'] == '!E0\n!E5\n!E10\n!E15\n!E20\n!E25\n'
    else:
        sh_script = codeblock(
            r'''
            for i in `seq 0 15`;
            do
                sleep .000001
                >&1 echo "O$i"
                if [ "$(($i % 5))" = "0" ]; then
                    >&2 echo "!E$i"
                fi
            done
            ''').lstrip()
        result = cmd(sh_script, shell=True, verbose=0)

        assert result['out'] == 'O0\nO1\nO2\nO3\nO4\nO5\nO6\nO7\nO8\nO9\nO10\nO11\nO12\nO13\nO14\nO15\n'
        assert result['err'] == '!E0\n!E5\n!E10\n!E15\n'


@pytest.mark.skipif(sys.platform == 'win32', reason='does not run on win32')
def test_cmd_interleaved_streams_py():
    # apparently multiline quotes dont work on win32
    if False:
        # slow mode
        py_script = codeblock(
            r'''
            python -c "
            import sys
            import time
            for i in range(30):
                time.sleep(.001)
                sys.stdout.write('O{}\n'.format(i))
                sys.stdout.flush()
                if i % 5 == 0:
                    sys.stderr.write('!E{}\n'.format(i))
                    sys.stderr.flush()
            "
            ''').lstrip()
        result = cmd(py_script, verbose=0)

        assert result['out'] == 'O0\nO1\nO2\nO3\nO4\nO5\nO6\nO7\nO8\nO9\nO10\nO11\nO12\nO13\nO14\nO15\nO16\nO17\nO18\nO19\nO20\nO21\nO22\nO23\nO24\nO25\nO26\nO27\nO28\nO29\n'
        assert result['err'] == '!E0\n!E5\n!E10\n!E15\n!E20\n!E25\n'
    else:
        # faster mode
        py_script = codeblock(
            r'''
            python -c "
            import sys
            import time
            for i in range(15):
                time.sleep(.000001)
                sys.stdout.write('O{}\n'.format(i))
                sys.stdout.flush()
                if i % 5 == 0:
                    sys.stderr.write('!E{}\n'.format(i))
                    sys.stderr.flush()
            "
            ''').lstrip()
        result = cmd(py_script, verbose=0)

        assert result['out'] == 'O0\nO1\nO2\nO3\nO4\nO5\nO6\nO7\nO8\nO9\nO10\nO11\nO12\nO13\nO14\n'
        assert result['err'] == '!E0\n!E5\n!E10\n'


def test_cwd():
    import sys
    import os
    if not sys.platform.startswith('win32'):
        dpath = ensure_app_resource_dir('boltons')
        dpath = os.path.realpath(dpath)
        info = cmd('pwd', cwd=dpath, shell=True)
        # print('info = {}'.format(repr2(info, nl=1)))
        print('info = {}'.format(repr(info)))
        print('dpath = {!r}'.format(dpath))
        assert info['out'].strip() == dpath


def test_env():
    import sys
    import os
    if not sys.platform.startswith('win32'):
        env = os.environ.copy()
        env.update({'UBELT_TEST_ENV': '42'})
        info = cmd('echo $UBELT_TEST_ENV', env=env, shell=True)
        print(info['out'])
        assert info['out'].strip() == env['UBELT_TEST_ENV']


if __name__ == '__main__':
    import xdoctest
    xdoctest.doctest_module(__file__)
