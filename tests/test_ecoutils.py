import os
import socket
import sys

from boltons import ecoutils


def test_basic():
    # basic sanity test
    prof = ecoutils.get_profile()

    assert prof['python']['bin'] == sys.executable


def test_scrub():
    prof = ecoutils.get_profile(scrub=True)

    assert prof['username'] == '-'
    assert prof['hostname'] == '-'
    assert prof['hostfqdn'] == '-'
    assert prof['cwd'] == '-'
    assert prof['uname']['node'] == '-'
    assert prof['python']['bin'] == '-'
    assert prof['python']['argv'] == '-'


def test_scrub_does_not_resolve_the_host(monkeypatch):
    def unreachable(*args):
        raise AssertionError('scrubbed profile resolved the host name')

    monkeypatch.setattr(socket, 'gethostname', unreachable)
    monkeypatch.setattr(socket, 'getfqdn', unreachable)

    prof = ecoutils.get_profile(scrub=True)

    assert prof['hostname'] == '-'
    assert prof['hostfqdn'] == '-'


def test_scrub_does_not_read_the_cwd(monkeypatch):
    calls = []
    real_getcwd = os.getcwd

    def recording_getcwd():
        calls.append('getcwd')
        return real_getcwd()

    monkeypatch.setattr(os, 'getcwd', recording_getcwd)

    prof = ecoutils.get_profile(scrub=True)

    assert calls == []

    assert prof['cwd'] == '-'
