import importlib.util
import os
import socket
import sys

import pytest

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


@pytest.mark.parametrize('value', [0, 1, 16, 2 ** 128 - 1])
def test_instance_id_preserves_all_bits(monkeypatch, value):
    def getrandbits(self, count):
        assert count == 128
        return value

    monkeypatch.setattr(ecoutils.random.SystemRandom, 'getrandbits', getrandbits)
    spec = importlib.util.spec_from_file_location('test_ecoutils_instance', ecoutils.__file__)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    identifier = module.get_profile(scrub=True)['guid']
    assert len(identifier) == 32
    assert int(identifier, 16) == value


@pytest.mark.parametrize('mask', [0o002, 0o022, 0o077, 0o777])
def test_profile_umask_octal_digits(monkeypatch, mask):
    calls = []

    def umask(value):
        calls.append(value)
        return mask

    monkeypatch.setattr(os, 'umask', umask)
    prof = ecoutils.get_profile(scrub=True)
    assert prof['umask'] == format(mask, '03o')
    assert calls == [2, mask]
