import os.path
import pytest

from boltons import fileutils
from boltons.fileutils import FilePerms, iter_find_files, DummyFile
from boltons.strutils import removeprefix


BOLTONS_PATH = os.path.dirname(os.path.abspath(fileutils.__file__))


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


def test_iter_find_files():
    def _to_baseless_list(paths):
        return [removeprefix(p, BOLTONS_PATH).lstrip(os.path.sep) for p in paths]

    assert 'fileutils.py' in _to_baseless_list(iter_find_files(BOLTONS_PATH, patterns=['*.py']))

    boltons_parent = os.path.dirname(BOLTONS_PATH)
    assert 'fileutils.py' in _to_baseless_list(iter_find_files(boltons_parent, patterns=['*.py']))
    assert 'fileutils.py' not in _to_baseless_list(iter_find_files(boltons_parent, patterns=['*.py'], max_depth=0))


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
    for i in range(1, 5):
        cur_path = tmp_path / f'test_file.{i}.txt'
        cur_path.write_text(f'test content {i}')
        assert cur_path.exists()

    fileutils.rotate_file(file_path, keep=5)
    assert not file_path.exists()

    for i in range(1, 5):
        cur_path = tmp_path / f'test_file.{i}.txt'
        assert cur_path.read_text() == f'test content {i-1}'

    assert not (tmp_path / 'test_file.5.txt').exists()

def test_rotate_file_full_rotation_no_ext(tmp_path):
    file_path = tmp_path / 'test_file'
    file_path.write_text('test content 0')
    for i in range(1, 5):
        cur_path = tmp_path / f'test_file.{i}'
        cur_path.write_text(f'test content {i}')
        assert cur_path.exists()

    fileutils.rotate_file(file_path, keep=5)
    assert not file_path.exists()

    for i in range(1, 5):
        cur_path = tmp_path / f'test_file.{i}'
        assert cur_path.read_text() == f'test content {i-1}'

    assert not (tmp_path / 'test_file.5').exists()

def test_dummy_file_text_mode():
    df = DummyFile('/dev/null', 'w')
    
    # Test basic operations
    assert df.mode == 'w'
    assert not df.closed
    
    # Test text operations
    df.write('test')
    df.writelines(['line1\n', 'line2\n'])
    
    # Test read operations return empty strings
    assert df.read() == ''
    assert df.readline() == ''
    assert df.readlines() == []
    
    # Test type checking
    with pytest.raises(TypeError):
        df.write(b'bytes not allowed in text mode')
    with pytest.raises(TypeError):
        df.writelines([b'bytes not allowed\n'])

def test_dummy_file_binary_mode():
    df = DummyFile('/dev/null', 'wb')
    
    # Test basic operations
    assert df.mode == 'wb'
    assert not df.closed
    
    # Test binary operations
    df.write(b'test')
    df.writelines([b'line1\n', b'line2\n'])
    
    # Test read operations return empty bytes
    assert df.read() == b''
    assert df.readline() == b''
    assert df.readlines() == []
    
    # Test type checking
    with pytest.raises(TypeError):
        df.write('text not allowed in binary mode')
    with pytest.raises(TypeError):
        df.writelines(['text not allowed\n'])

def test_dummy_file_closed():
    df = DummyFile('/dev/null')
    df.close()
    assert df.closed
    
    # All operations should raise ValueError when closed
    with pytest.raises(ValueError):
        df.read()
    with pytest.raises(ValueError):
        df.write('test')
    with pytest.raises(ValueError):
        df.writelines(['test'])
    with pytest.raises(ValueError):
        df.seek()
    with pytest.raises(ValueError):
        df.tell()
    with pytest.raises(ValueError):
        df.flush()
    with pytest.raises(ValueError):
        df.truncate()

def test_dummy_file_context_manager():
    with DummyFile('/dev/null', 'w') as df:
        df.write('test')
        assert not df.closed
    
    # File should be usable after context exit
    assert not df.closed
    df.write('more text')

def test_dummy_file_iteration():
    df = DummyFile('/dev/null')
    
    # Test iteration methods
    with pytest.raises(StopIteration):
        next(df)
    with pytest.raises(StopIteration):
        df.__next__()
    
    # Test as iterator
    assert list(df) == []

