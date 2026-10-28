import pytest

from boltons.socketutils import BufferedSocket


class Socket:
    def __init__(self):
        self.reads = 0
        self.timeouts = []

    def settimeout(self, timeout):
        self.timeouts.append(timeout)

    def recv(self, size):
        self.reads += 1
        return b"abcd"


@pytest.mark.parametrize("method", ["recv", "recv_size", "peek"])
@pytest.mark.parametrize("buffer", [b"", b"abcd"])
@pytest.mark.parametrize("size,error", [(-1, ValueError), (1.5, TypeError)])
def test_invalid_read_size_preserves_socket_and_buffer(method, buffer, size, error):
    sock = Socket()
    stream = BufferedSocket(sock, timeout=1)
    stream.rbuf = buffer
    with pytest.raises(error):
        getattr(stream, method)(size)
    assert stream.rbuf == buffer
    assert sock.reads == 0
    assert sock.timeouts == []


class Index:
    def __index__(self):
        return 2


@pytest.mark.parametrize("method", ["recv", "recv_size", "peek"])
@pytest.mark.parametrize("buffer", [b"", b"abcd"])
def test_read_size_accepts_index_protocol(method, buffer):
    sock = Socket()
    stream = BufferedSocket(sock, timeout=1)
    stream.rbuf = buffer
    assert getattr(stream, method)(Index()) == b"ab"
    assert stream.rbuf == (b"abcd" if method == "peek" else b"cd")
