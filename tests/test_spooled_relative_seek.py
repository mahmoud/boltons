import os

import pytest

from boltons.ioutils import SpooledStringIO


@pytest.mark.parametrize("rolled", [False, True])
def test_relative_backwards_seek_uses_character_position(rolled):
    with SpooledStringIO() as stream:
        stream.write("a☃bc")
        if rolled:
            stream.rollover()
        stream.seek(3)
        assert stream.seek(-2, os.SEEK_CUR) == 1
        assert stream.read(2) == "☃b"
        assert stream.tell() == 3


@pytest.mark.parametrize("rolled", [False, True])
@pytest.mark.parametrize("offset,whence", [(-1, os.SEEK_SET), (-3, os.SEEK_CUR)])
def test_negative_destination_rejected_without_moving(rolled, offset, whence):
    with SpooledStringIO() as stream:
        stream.write("a☃bc")
        if rolled:
            stream.rollover()
        stream.seek(2)
        with pytest.raises(ValueError):
            stream.seek(offset, whence)
        assert stream.tell() == 2
        assert stream.read() == "bc"
