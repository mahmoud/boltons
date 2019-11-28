# -*- coding: utf-8 -*-
r"""
This module defines the :func:`cmd` command, which provides a simple means for
interacting with the commandline. While this does use :class:`subprocess.Popen`
under the hood, the key draw of :func:`cmd` is that you can capture
stdout/stderr in your program while simultaneously printing it to the terminal
in real time.

Example:
    >>> from boltons.cmdutils import cmd
    >>> # Running with verbose=1 will write to stdout in real time
    >>> info = cmd('echo "write your command naturally"', verbose=1)
    write your command naturally
    >>> # Unless `detatch=True`, `cmd` always returns an info dict.

    print('info = ' + repr(info))  # xdoctest: +IGNORE_WANT
    info = {
        'command': 'echo "write your command naturally"',
        'cwd': None,
        'err': '',
        'out': 'write your command naturally\n',
        'proc': <subprocess.Popen object at ...>,
        'ret': 0,
    }
"""
from __future__ import absolute_import, division, print_function, unicode_literals
import sys
import six

POSIX = 'posix' in sys.builtin_module_names

if POSIX:
    import select
else:  # nocover
    select = NotImplemented

__all__ = ['cmd']


def _textio_iterlines(stream):
    """
    Iterates over lines in a TextIO stream until an EOF is encountered.
    This is the iterator version of stream.readlines()
    """
    line = stream.readline()
    while line != '':
        yield line
        line = stream.readline()


def _proc_async_iter_stream(proc, stream, buffersize=1):
    """
    Reads output from a process in a separate thread
    """
    from six.moves import queue
    from threading import Thread
    def enqueue_output(proc, stream, stream_queue):
        while proc.poll() is None:
            line = stream.readline()
            # print('ENQUEUE LIVE {!r} {!r}'.format(stream, line))
            stream_queue.put(line)

        for line in _textio_iterlines(stream):
            # print('ENQUEUE FINAL {!r} {!r}'.format(stream, line))
            stream_queue.put(line)

        # print("STREAM IS DONE {!r}".format(stream))
        stream_queue.put(None)  # signal that the stream is finished
        # stream.close()
    stream_queue = queue.Queue(maxsize=buffersize)
    _thread = Thread(target=enqueue_output, args=(proc, stream, stream_queue))
    _thread.daemon = True  # thread dies with the program
    _thread.start()
    return stream_queue


def _proc_iteroutput_thread(proc):
    """
    Iterates over output from a process line by line

    Note:
        WARNING. Current implementation might have bugs with other threads.
        This behavior was seen when using earlier versions of tqdm. I'm not
        sure if this was our bug or tqdm's. Newer versions of tqdm fix this,
        but I cannot guarantee that there isn't an issue on our end.

    Yields:
        Tuple[str, str]: oline, eline: stdout and stderr line

    References:
        https://stackoverflow.com/questions/375427/non-blocking-read-subproc
    """
    from six.moves import queue

    # Create threads that read stdout / stderr and queue up the output
    stdout_queue = _proc_async_iter_stream(proc, proc.stdout)
    stderr_queue = _proc_async_iter_stream(proc, proc.stderr)

    stdout_live = True
    stderr_live = True

    # read from the output asynchronously until
    while stdout_live or stderr_live:
        if stdout_live:  # pragma: nobranch
            try:
                oline = stdout_queue.get_nowait()
                stdout_live = oline is not None
            except queue.Empty:
                oline = None
        if stderr_live:
            try:
                eline = stderr_queue.get_nowait()
                stderr_live = eline is not None
            except queue.Empty:
                eline = None
        if oline is not None or eline is not None:
            yield oline, eline


def _proc_iteroutput_select(proc):
    """
    Iterates over output from a process line by line

    UNIX only. Use :func:`_proc_iteroutput_thread` instead for a cross platform
    solution based on threads.

    Yields:
        Tuple[str, str]: oline, eline: stdout and stderr line
    """
    from six.moves import zip_longest
    # Read output while the external program is running
    while proc.poll() is None:
        reads = [proc.stdout.fileno(), proc.stderr.fileno()]
        ret = select.select(reads, [], [])
        oline = eline = None
        for fd in ret[0]:
            if fd == proc.stdout.fileno():
                oline = proc.stdout.readline()
            if fd == proc.stderr.fileno():
                eline = proc.stderr.readline()
        yield oline, eline

    # Grab any remaining data in stdout and stderr after the process finishes
    oline_iter = _textio_iterlines(proc.stdout)
    eline_iter = _textio_iterlines(proc.stderr)
    for oline, eline in zip_longest(oline_iter, eline_iter):
        yield oline, eline


def _tee_output(proc, stdout=None, stderr=None, backend='auto'):
    """
    Simultaneously reports and captures stdout and stderr from a process

    subprocess must be created using (stdout=subprocess.PIPE,
    stderr=subprocess.PIPE)
    """
    logged_out = []
    logged_err = []
    if backend == 'auto':
        # backend = 'select' if POSIX else 'thread'
        backend = 'thread'

    if backend == 'select':
        if not POSIX:  # nocover
            raise NotImplementedError('select is only available on posix')
        # the select-based version is stable, but slow
        _proc_iteroutput = _proc_iteroutput_select
    elif backend == 'thread':
        # the thread version is fast, but might run into issues.
        _proc_iteroutput = _proc_iteroutput_thread
    else:
        raise ValueError('backend must be select, thread, or auto')

    for oline, eline in _proc_iteroutput(proc):
        if oline:
            if stdout:  # pragma: nobranch
                stdout.write(oline)
                stdout.flush()
            logged_out.append(oline)
        if eline:
            if stderr:  # pragma: nobranch
                stderr.write(eline)
                stderr.flush()
            logged_err.append(eline)
    return proc, logged_out, logged_err


def cmd(command, shell=False, detach=False, cwd=None,
        env=None, tee=None, tee_backend='auto', verbose=0):
    """
    Executes a command in a subprocess.

    The advantage of this wrapper around subprocess is that
    (1) you control if the subprocess prints to stdout,
    (2) the text written to stdout and stderr is returned for parsing,
    (3) cross platform behavior that lets you specify the command as a string
    or tuple regardless of whether or not shell=True.
    (4) ability to detach, return the process object and allow the process to
    run in the background (eventually we may return a Future object instead).

    Implementation is based on the collection of code samples on stackoverflow
    [1]_ [2]_ [3]_.


    Args:
        command (str or Sequence): bash-like command string or tuple of
            executable and args

        shell (bool, default=False): if True, process is run in shell.

        detach (bool, default=False):
            if True, process is detached and run in background.

        cwd (PathLike, optional): path to run command

        env (str, optional): environment passed to Popen

        tee (bool, optional): if True, simultaneously writes to stdout while
            capturing output from the command. If not specified, defaults to
            True if verbose > 0.  If detach is True, then this argument is
            ignored.

        tee_backend (str, optional): backend for tee output.
            Valid choices are: "auto", "select" (POSIX only), and "thread".

        verbose (int, default=0): verbosity mode. Can be 0, 1, 2, or 3.
            0 is quiet, 3 is loud.

    Returns:
        dict: info - information about command status.
            if detach is False ``info`` contains captured standard out,
            standard error, and the return code
            if detach is False ``info`` contains a reference to the process.

    Notes:

        * While this function strives to be cross-platform, there are certain
          insurmountable issues that ar/se when handling multiple shell
          languages.

        * Inputs can either be text or tuple based. On UNIX we ensure
            conversion to text if shell=True, and to tuple if shell=False. On
            windows, the input is always text based.  See [3]_ for a potential
            cross-platform shlex solution for windows.

    References:
        .. [1] https://stackoverflow.com/questions/11495783/redirect-subprocess-stderr-to-stdout
        .. [2] https://stackoverflow.com/questions/7729336/display-subprocess-stdout-without-distorti
        .. [3] https://stackoverflow.com/questions/33560364/python-windows-parsing-command-lines-with-shlex

    Example:
        >>> info = cmd(('echo', 'simple cmdline interface'), verbose=1)
        simple cmdline interface

        print(info)  # xdoctest: +IGNORE_WANT
        {'out': 'simple cmdline interface\n',
         'err': '',
         'ret': 0,
         'proc': <subprocess.Popen at 0x7f0a4723a2e8>,
         'cwd': None,
         'command': "echo 'simple cmdline interface'"}

        >>> # The following commands demonstrate multiple ways co call cmd
        >>> info = cmd('echo str noshell', verbose=0)
        >>> assert info['out'].strip() == 'str noshell'

        >>> # windows echo will output extra single quotes
        >>> info = cmd(('echo', 'tuple noshell'), verbose=0)
        >>> assert info['out'].strip().strip("'") == 'tuple noshell'

        >>> # Note this command is formatted to work on win32 and unix
        >>> info = cmd('echo str&&echo shell', verbose=0, shell=True)
        >>> assert info['out'].strip() == 'str' + chr(10) + 'shell'

        >>> info = cmd(('echo', 'tuple shell'), verbose=0, shell=True)
        >>> assert info['out'].strip().strip("'") == 'tuple shell'
    """
    # Determine if command is specified as text or a tuple
    if isinstance(command, six.string_types):
        command_text = command
        command_tup = None
    else:
        import pipes
        command_tup = command
        command_text = ' '.join(list(map(pipes.quote, command_tup)))

    if shell or sys.platform.startswith('win32'):
        # When shell=True, args is sent to the shell (e.g. bin/sh) as text
        args = command_text

        if sys.version_info[0] == 2 and sys.version_info[1] < 7:
            # for python 2.6
            try:
                args = args.decode()
            except Exception:
                pass
    else:
        # When shell=False, args is a list of executable and arguments
        if command_tup is None:
            # parse this out of the string
            # NOTE: perhaps use the solution from [3] here?
            import shlex
            command_tup = shlex.split(command_text)
            args = command_text
            # command_tup = shlex.split(command_text, posix=not WIN32)
        args = command_tup

        if sys.version_info[0] == 2 and sys.version_info[1] < 7:
            # for python 2.6
            try:
                args = tuple([a.decode() for a in args])
            except Exception:
                pass

    if tee is None:
        tee = verbose > 0
    if verbose > 1:
        import os
        import platform
        if verbose > 2:
            try:
                print('┌─── START CMD ───')
            except Exception:  # nocover
                print('+=== START CMD ===')
        cwd_ = os.getcwd() if cwd is None else cwd
        compname = platform.node()
        try:
            import getpass
            username = getpass.getuser()
        except Exception:
            username = ''

        cwd_ = _shrinkuser(cwd_)
        ps1 = '[cmd] {0}@{1}:{2}$ '.format(username, compname, cwd_)
        print(ps1 + command_text)

    # Create a new process to execute the command
    def make_proc():
        # delay the creation of the process until we validate all args
        import subprocess
        popen_kw = dict(
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, shell=shell,
            universal_newlines=True, cwd=cwd, env=env)
        proc = subprocess.Popen(args, **popen_kw)
        return proc

    if detach:
        info = {'proc': make_proc(), 'command': command_text}
        if verbose > 0:  # nocover
            print('...detaching')
    else:
        if tee:
            # We logging stdout and stderr, while simulaniously piping it to
            # another stream.
            stdout = sys.stdout
            stderr = sys.stderr
            proc = make_proc()
            proc, logged_out, logged_err = _tee_output(proc, stdout, stderr,
                                                       backend=tee_backend)

            try:
                out = ''.join(logged_out)
            except UnicodeDecodeError:  # nocover
                out = '\n'.join(_.decode('utf-8') for _ in logged_out)
            try:
                err = ''.join(logged_err)
            except UnicodeDecodeError:  # nocover
                err = '\n'.join(_.decode('utf-8') for _ in logged_err)
            (out_, err_) = proc.communicate()
        else:
            proc = make_proc()
            (out, err) = proc.communicate()
        # calling wait means that the process will terminate and it is safe to
        # return a reference to the process object.
        ret = proc.wait()
        info = {
            'out': out,
            'err': err,
            'ret': ret,
            'proc': proc,
            'cwd': cwd,
            'command': command_text
        }
        if verbose > 2:
            # https://en.wikipedia.org/wiki/Box-drawing_character
            try:
                print('└─── END CMD ───')
            except Exception:  # nocover
                print('L___ END CMD ___')
    return info


def _shrinkuser(path, home='~'):
    """
    Internal version of :func:`boltons.pathutils.strinkuser'
    """
    from os.path import expanduser, normpath
    import os
    path = normpath(path)
    userhome_dpath = expanduser('~')
    if path.startswith(userhome_dpath):
        if len(path) == len(userhome_dpath):
            path = home
        elif path[len(userhome_dpath)] == os.path.sep:
            path = home + path[len(userhome_dpath):]
    return path


if __name__ == '__main__':
    """
    CommandLine:
        python ~/code/boltons/boltons/cmdutils.py all
    """
    import xdoctest
    xdoctest.doctest_module(__file__)
