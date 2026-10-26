import os.path
import pathlib

import pytest



from boltons import fileutils
from boltons.fileutils import FilePerms, iter_find_files
from boltons.strutils import removeprefix


BOLTONS_PATH = os.path.dirname(os.path.abspath(fileutils.__file__))


@pytest.mark.parametrize('rm_part_on_exc', [False, True])
@pytest.mark.parametrize('phase', ['cloexec', 'fdopen', 'chmod'])
def test_atomicsaver_setup_failure_cleans_owned_resources(tmp_path, monkeypatch,
                                                       rm_part_on_exc, phase):
    dest = tmp_path / 'output.bin'
    dest.write_bytes(b'original')
    saver = fileutils.AtomicSaver(dest, rm_part_on_exc=rm_part_on_exc)
    failure = OSError('setup failed')
    descriptors = []
    real_open = os.open

    def track_open(*args, **kwargs):
        fd = real_open(*args, **kwargs)
        descriptors.append(fd)
        return fd

    def fail(*args, **kwargs):
        raise failure

    monkeypatch.setattr(os, 'open', track_open)
    if phase == 'cloexec':
        monkeypatch.setattr(fileutils, 'set_cloexec', fail)
    else:
        monkeypatch.setattr(os, phase, fail)

    try:
        with pytest.raises(OSError) as caught:
            with saver:
                pytest.fail('context body must not run after setup failure')
        assert caught.value is failure
        with pytest.raises(OSError):
            os.fstat(descriptors[0])
        assert os.path.exists(saver.part_path) is (not rm_part_on_exc)
        assert dest.read_bytes() == b'original'
    finally:
        # Keep a failing regression from leaking its real descriptor.
        if saver.part_file is not None:
            saver.part_file.close()
        else:
            try:
                os.close(descriptors[0])
            except OSError:
                pass


def test_atomicsaver_setup_failure_preserves_existing_part(tmp_path):
    dest = tmp_path / 'output.bin'
    part = tmp_path / 'output.bin.part'
    part.write_bytes(b'from another writer')
    with pytest.raises(OSError):
        with fileutils.AtomicSaver(dest):
            pytest.fail('existing part must not be overwritten')
    assert part.read_bytes() == b'from another writer'


def test_atomicsaver_unbuffered_text_setup_cleanup(tmp_path):
    dest = tmp_path / 'output.txt'
    with pytest.raises(ValueError, match='unbuffered text'):
        with fileutils.AtomicSaver(dest, text_mode=True, buffering=0):
            pytest.fail('invalid buffering must fail at setup')
    assert list(tmp_path.iterdir()) == []


def test_atomicsaver_setup_cleanup_error_preserves_setup_error(tmp_path, monkeypatch):
    dest = tmp_path / 'output.bin'
    saver = fileutils.AtomicSaver(dest)
    failure = OSError('setup failed')

    def fail_cloexec(fd):
        raise failure

    def fail_unlink(path):
        raise OSError('cleanup failed')

    monkeypatch.setattr(fileutils, 'set_cloexec', fail_cloexec)
    monkeypatch.setattr(os, 'unlink', fail_unlink)
    with pytest.raises(OSError) as caught:
        saver.setup()
    assert caught.value is failure


def test_fileperms():
    up = FilePerms()
    up.other = ''
    up.user = 'xrw'
    up.group = 'rrrwx'
    try:
        up.other = 'nope'
    except ValueError:
        # correctly raised ValueError on invalid chars
        pass

    assert repr(up) == "FilePerms(user='rwx', group='rwx', other='')"
    assert up.user == 'rwx'
    assert oct(int(up)) == '0o770'

    assert int(FilePerms()) == 0


def test_fileperms_from_int_leading_zero_groups():
    assert int(FilePerms.from_int(0o007)) == 0o007
    assert FilePerms.from_int(0o070).group == 'rwx'
    assert FilePerms.from_int(0o070).user == ''


def test_fileperms_revoke():
    fp = FilePerms(user='rw', other='r')
    fp.other = ''
    assert int(fp) == 0o600
    fp.user = 'r'
    assert int(fp) == 0o400


class _FlushFailingFile:
    def __init__(self, f):
        self.f = f

    def write(self, data):
        return self.f.write(data)

    def fileno(self):
        return self.f.fileno()

    def flush(self):
        raise OSError('simulated flush failure')

    def close(self):
        self.f.close()


class _FlushFailingSaver(fileutils.AtomicSaver):
    def _open_part_file(self):
        super()._open_part_file()
        self.real_part_file = self.part_file
        self.part_file = _FlushFailingFile(self.real_part_file)


def test_atomicsaver_flush_failure_cleans_up(tmp_path):
    dest = tmp_path / 'output.bin'
    saver = _FlushFailingSaver(str(dest))
    try:
        with saver as f:
            f.write(b'data')
    except OSError as e:
        assert 'simulated flush failure' in str(e)
    else:
        raise AssertionError('expected OSError from flush')
    assert saver.real_part_file.closed
    assert not os.path.exists(saver.part_path)
    assert not dest.exists()



def test_atomicsaver_pathlike(tmp_path):
    dest = tmp_path / 'output.bin'
    with fileutils.AtomicSaver(dest) as f:
        f.write(b'pathlike works')
    assert dest.read_bytes() == b'pathlike works'


def test_iter_find_files_pathlike():
    boltons_path = pathlib.Path(BOLTONS_PATH)
    results = list(iter_find_files(boltons_path, patterns=['*.py']))
    basenames = [os.path.basename(p) for p in results]
    assert 'fileutils.py' in basenames


def test_iter_find_files():
    def _to_baseless_list(paths):
        return [removeprefix(p, BOLTONS_PATH).lstrip(os.path.sep) for p in paths]

    assert 'fileutils.py' in _to_baseless_list(iter_find_files(BOLTONS_PATH, patterns=['*.py']))

    boltons_parent = os.path.dirname(BOLTONS_PATH)
    assert 'fileutils.py' in _to_baseless_list(iter_find_files(boltons_parent, patterns=['*.py']))
    assert 'fileutils.py' not in _to_baseless_list(iter_find_files(boltons_parent, patterns=['*.py'], max_depth=0))


def test_iter_find_files_trailing_sep(tmp_path):
    sub2 = tmp_path / 'sub' / 'sub2'
    sub2.mkdir(parents=True)
    for path in (tmp_path / 'a.txt', tmp_path / 'sub' / 'b.txt', sub2 / 'c.txt'):
        path.write_text('x')

    def _names(directory):
        return sorted(os.path.basename(p) for p in
                      iter_find_files(directory, '*.txt', max_depth=1))

    assert _names(str(tmp_path)) == ['a.txt', 'b.txt']
    assert _names(str(tmp_path) + os.path.sep) == ['a.txt', 'b.txt']


def test_rotate_file_no_rotation(tmp_path):
    file_path = tmp_path / 'test_file.txt'
    fileutils.rotate_file(file_path)
    assert not file_path.exists()


def test_rotate_file_one_rotation(tmp_path):
    file_path = tmp_path / 'test_file.txt'
    file_path.write_text('test content')
    assert file_path.exists()

    fileutils.rotate_file(file_path)
    assert not file_path.exists()
    assert (tmp_path / 'test_file.1.txt').exists()


def test_rotate_file_full_rotation(tmp_path):
    file_path = tmp_path / 'test_file.txt'
    file_path.write_text('test content 0')
    for i in range(1, 6):
        cur_path = tmp_path / f'test_file.{i}.txt'
        cur_path.write_text(f'test content {i}')
        assert cur_path.exists()

    fileutils.rotate_file(file_path, keep=5)
    assert not file_path.exists()

    for i in range(1, 6):
        cur_path = tmp_path / f'test_file.{i}.txt'
        assert cur_path.read_text() == f'test content {i-1}'

    assert not (tmp_path / 'test_file.6.txt').exists()

def test_rotate_file_full_rotation_no_ext(tmp_path):
    file_path = tmp_path / 'test_file'
    file_path.write_text('test content 0')
    for i in range(1, 6):
        cur_path = tmp_path / f'test_file.{i}'
        cur_path.write_text(f'test content {i}')
        assert cur_path.exists()

    fileutils.rotate_file(file_path, keep=5)
    assert not file_path.exists()

    for i in range(1, 6):
        cur_path = tmp_path / f'test_file.{i}'
        assert cur_path.read_text() == f'test content {i-1}'

    assert not (tmp_path / 'test_file.6').exists()


def test_rotate_file_keep_one(tmp_path):
    # keep=1 used to delete the backup it had just made
    file_path = tmp_path / 'log.txt'
    for gen in range(3):
        file_path.write_text(f'gen {gen}')
        fileutils.rotate_file(file_path, keep=1)
        assert sorted(p.name for p in tmp_path.iterdir()) == ['log.1.txt']
        assert (tmp_path / 'log.1.txt').read_text() == f'gen {gen}'

