
"""Utility functions for working with other processes"""


"""A helper function for common uses of subprocess

This aims to make some commonly desired functionality easier to do without needing
to manually create Popen objects, while being more flexible than check_call() and check_output().

Should work fine with gevent.subprocess with monkey patching.
"""

import os
import signal
import sys
import weakref
from subprocess import PIPE, Popen, CalledProcessError

IS_PY2 = sys.version_info[0] == 2

def _raise(ex_type, ex, tb):
    # py3 compat
    if IS_PY2:
        # wrap in exec() so we don't parse unless we need to (prevent SyntaxError in py3)
        exec('raise ex_type, ex, tb')
    else:
        raise ex


def cmd(args, return_stdout=True, return_stderr=False, return_code=False, return_proc=False,
        stdin=None, stdout=PIPE, stderr=PIPE, success=0, cwd=None, close_fds=True, env={}, clear_env=False):
    r"""Run a command, blocking until it exits.
    By default, returns the command's stdout as a string.
    First argument "args" should be either a list of arguments,
    or a string (which will be subject to shell interpretation).
    If the process exits non-zero, raises a CommandFailedError (which is a customised CalledProcessError).

    This function is intended as a more powerful version of subprocess.call() and friends,
    with better error reporting and default behaviour.
    Note that this function only supports POSIX platforms.

    Simple usage:
        >>> cmd(['echo', 'hello world'])
        'hello world\n'

    A note on return values:
        By default, only stdout is returned.
        The return_* flags change this behaviour.
        If the flags are set such that more than one item is to be returned, they are returned
        as a tuple in the following order: (stdout, stderr, retcode, proc), omitting anything not to be returned.
        For example, return_stdout=True and return_proc=True would return (stdout, proc).
        If nothing at all is to be returned, None is returned.

    Keyword options are as follows:
        return_stdout, return_stderr: Flag for whether stdout/stderr should be returned.
                                      If they weren't captured (see stdout, stderr options), None is returned.
                                      Defaults are True for stdout, False for stderr.
        return_code: Flag for whether to return the exit code of the process. Default False.
        return_proc: Flag for whether the underlying subprocess.Popen object should be returned. Default False.
        stdin: Any of the following (default: None):
            A file-like object or file descriptor: Use given fd as stdin.
            A string: Pass string to process as stdin.
            None: Set stdin to /dev/null
        stdout: Any of the following (default: subprocess.PIPE):
            A file-like object or file descriptor: Use given fd as stdout.
            subprocess.PIPE: Allows cmd() to collect the output and return it (if return_stdout=True).
                             NOTE: If this argument is not given, any returned stdout will be set to None.
            None: Set stdout to /dev/null
        stderr: As stdout. Takes an additional option, subprocess.STDOUT, which causes stderr to be interleaved
                with stdout. Default subprocess.PIPE.
        success: Determines what constitutes a command success (ie. what will not cause a CommandFailedError):
            int, iterable of int: Exit code or codes that mean success.
            'any': Consider any condition at all a success, ie. never raise.
            'nosignal': Succeed if the program cleanly exited, ie. was not killed by a signal.
            callable: Takes (stdout, stderr, retcode) as args and should return True to indicate success.
            The default value is 0, ie. any non-zero exit is considered a failure.
        cwd: As per subprocess.Popen()
        close_fds: As per subprocess.Popen(), except we default to True.
        env: Environment variables to set in addition to the current environment. NOTE that this differs
             from subprocess.Popen()'s behaviour, which will not include any of the current environment if env
             is set. Default {}.
        clear_env: If True, do not include any of the current environment variables. Default False.

    An example of a more complex usage:
        >>> cmd('read input; echo foo; echo $input >&2; exit $BAZ',
        ...     stdin='bar', stdout=None, return_stderr=True, success=[0,1], env={"BAZ": 1})
        (None, 'bar\n')

    An example similar to subprocess.call(), re-using the parent's stdin/out/err as per subprocess' defaults:
        >>> cmd(["echo", "hello"], stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr,
        ...     return_stdout=False, return_code=True) # doctest: +SKIP
        hello
        0

    """

    if os.name != 'posix':
        raise NotImplementedError("cmd() only supports posix platforms")

    # normalise args to be all strings, determine shell
    if isinstance(args, basestring):
        shell = True
    else:
        args = map(str, args)
        shell = False

    # normalise env, clear_env to single dict
    env = dict((str(k), str(v)) for k, v in env.items())
    if not clear_env:
        user_env = env
        env = os.environ.copy()
        env.update(user_env)

    # normalise success to callable
    if success == 'any':
        success = lambda out, err, code: True
    elif success == 'nosignal':
        success = lambda out, err, code: code >= 0
    elif not callable(success):
        try:
            iter(success)
        except TypeError:
            success = success,
        success_values = map(int, success)
        success = lambda out, err, code: code in success_values

    # normalise stdin, stdout, stderr to values appropriate for Popen
    if isinstance(stdin, basestring):
        stdin_text = stdin
        stdin = PIPE
    else:
        stdin_text = None
    if stdin is None:
        stdin = get_devnull()
    if stdout is None:
        stdout = get_devnull()
    if stderr is None:
        stderr = get_devnull()

    proc = None
    try:
        proc = Popen(args, stdin=stdin, stdout=stdout, stderr=stderr, close_fds=close_fds,
                     shell=shell, cwd=cwd, env=env)
        stdout, stderr = proc.communicate(stdin_text)
        exitcode = proc.wait()
    except BaseException:
        ex_type, ex, tb = sys.exc_info() # save for re-raise later
        if proc and proc.poll() is None:
            try:
                proc.kill()
            except OSError:
                pass
        _raise(ex_type, ex, tb)

    if not success(stdout, stderr, exitcode):
        raise FailedProcessError(args, stdout, stderr, exitcode)

    result_flags = [
        (stdout, return_stdout),
        (stderr, return_stderr),
        (exitcode, return_code),
        (proc, return_proc),
    ]
    results = tuple(value for value, flag in result_flags if flag)
    if len(results) == 0:
        results = None
    elif len(results) == 1:
        results, = results
    return results


class FailedProcessError(CalledProcessError):
    """A subtype of CalledProcessError with more detail about what failed and how."""

    def __init__(self, args, stdout, stderr, exitcode):
        self.args = args
        self.stdout = stdout
        self.stderr = stderr
        self.exitcode = exitcode

    def __str__(self):
        s = self.summary()
        if self.stdout:
            s += '\nSTDOUT:\n{}'.format(self.stdout.strip())
        if self.stderr:
            s += '\nSTDERR:\n{}'.format(self.stderr.strip())
        return s

    def summary(self):
        if self.exitcode >= 0:
            status = 'failed with exit code {}'.format(self.exitcode)
        else:
            SIGNALS = ((value, name) for name, value in signal.__dict__.items()
                       if name.startswith('SIG') and not name.startswith('SIG_'))
            signum = -self.exitcode
            status = 'was killed by {}'.format(SIGNALS.get(signum, "Unknown signal {}".format(signum)))
        return "Process {!r} {}".format(self.args, status)


_devnull_ref = None
def get_devnull():
    """A simple wrapper to allow multiple callers to share one open FD to /dev/null,
    while still playing nice with the GC"""
    global _devnull_ref
    if _devnull_ref:
        devnull = _devnull_ref()
        if devnull:
            return devnull
    devnull = open('/dev/null', 'w+')
    _devnull_ref = weakref.ref(devnull)
    return devnull

