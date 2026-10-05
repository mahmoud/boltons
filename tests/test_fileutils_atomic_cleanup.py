import errno
from pathlib import Path

import pytest

from boltons import fileutils


@pytest.mark.parametrize('operation', ['flush', 'fsync', 'close', 'rename'])
@pytest.mark.parametrize('rm_part_on_exc', [True, False])
@pytest.mark.parametrize('existing', [True, False])
def test_atomic_saver_finalization_failure(tmp_path, monkeypatch, operation,
                                         rm_part_on_exc, existing):
    destination = tmp_path / 'output.bin'
    if existing:
        destination.write_bytes(b'old data')
    saver = fileutils.AtomicSaver(destination, rm_part_on_exc=rm_part_on_exc)
    failure = OSError(errno.ENOSPC, 'simulated finalization failure')
    close = None

    try:
        with monkeypatch.context() as patch:
            with pytest.raises(OSError) as caught:
                with saver as stream:
                    close = stream.close
                    stream.write(b'new data')

                    def fail(*args, **kwargs):
                        if operation == 'close':
                            close()
                        raise failure

                    if operation == 'fsync':
                        patch.setattr(fileutils.os, 'fsync', fail)
                    elif operation == 'rename':
                        patch.setattr(fileutils, 'atomic_rename', fail)
                    else:
                        patch.setattr(stream, operation, fail)
        assert caught.value is failure
        assert stream.closed
        assert Path(saver.part_path).exists() is not rm_part_on_exc
        if existing:
            assert destination.read_bytes() == b'old data'
        else:
            assert not destination.exists()
        if not rm_part_on_exc and operation != 'flush':
            assert Path(saver.part_path).read_bytes() == b'new data'
    finally:
        if close is not None:
            close()


@pytest.mark.parametrize('rm_part_on_exc', [True, False])
def test_atomic_saver_body_failure(tmp_path, rm_part_on_exc):
    destination = tmp_path / 'output.bin'
    destination.write_bytes(b'old data')
    saver = fileutils.AtomicSaver(destination, rm_part_on_exc=rm_part_on_exc)
    failure = RuntimeError('body failed')
    with pytest.raises(RuntimeError) as caught:
        with saver as stream:
            stream.write(b'new data')
            raise failure
    assert caught.value is failure
    assert stream.closed
    assert destination.read_bytes() == b'old data'
    assert Path(saver.part_path).exists() is not rm_part_on_exc


@pytest.mark.parametrize('body_failure', [True, False])
def test_atomic_saver_unlink_failure_preserves_exception(tmp_path, monkeypatch,
                                                       body_failure):
    destination = tmp_path / 'output.bin'
    destination.write_bytes(b'old data')
    saver = fileutils.AtomicSaver(destination)
    failure = RuntimeError('original failure')

    def fail(*args, **kwargs):
        raise failure

    def fail_unlink(*args, **kwargs):
        raise OSError(errno.EACCES, 'cleanup failed')

    with monkeypatch.context() as patch:
        patch.setattr(fileutils.os, 'unlink', fail_unlink)
        with pytest.raises(RuntimeError) as caught:
            with saver as stream:
                stream.write(b'new data')
                if body_failure:
                    raise failure
                patch.setattr(fileutils, 'atomic_rename', fail)
    assert caught.value is failure
    assert stream.closed
    assert destination.read_bytes() == b'old data'
    assert Path(saver.part_path).read_bytes() == b'new data'


def test_atomic_saver_successful_overwrite(tmp_path):
    destination = tmp_path / 'output.bin'
    destination.write_bytes(b'old data')
    saver = fileutils.AtomicSaver(destination)
    with saver as stream:
        stream.write(b'new data')
    assert stream.closed
    assert destination.read_bytes() == b'new data'
    assert not Path(saver.part_path).exists()
