# -*- coding: utf-8 -*-

import time
import errno
import socket
import threading
from boltons.socketutils import (BufferedSocket,
                                 NetstringSocket,
                                 ConnectionClosed,
                                 NetstringMessageTooLong,
                                 MessageTooLong,
                                 Timeout)


def test_short_lines():
    for ms in (2, 4, 6, 1024, None):
        x, y = socket.socketpair()
        bs = BufferedSocket(x)
        y.sendall(b'1\n2\n3\n')
        assert bs.recv_until(b'\n', maxsize=ms) == b'1\n'
        assert bs.recv_until(b'\n', maxsize=ms) == b'2\n'
        y.close()
        assert bs.recv_close(maxsize=ms) == b'3\n'

        try:
            bs.recv_size(1)
        except ConnectionClosed:
            pass
        else:
            assert False, 'expected ConnectionClosed'
    return


def test_multibyte_delim():
    delim = b'\r\n'
    empty = b'' + delim
    small_one = b'1' + delim
    big_two = b'2' * 2048 + delim
    for ms in (3, 5, 1024, None):
        x, y = socket.socketpair()
        bs = BufferedSocket(x)

        y.sendall(empty)
        y.sendall(small_one)
        y.sendall(big_two)

        assert bs.recv_until(delim, maxsize=ms) == empty
        assert bs.recv_until(delim, maxsize=ms) == small_one
        try:
            assert bs.recv_until(delim, maxsize=ms) == big_two
        except MessageTooLong:
            if ms is None:
                assert False, 'unexpected MessageTooLong'
        else:
            if ms is not None:
                assert False, 'expected MessageTooLong'

    return


def test_split_delim():
    delim = b'\r\n'
    first = b'1234\r'
    second = b'\n5'

    x, y = socket.socketpair()
    bs = BufferedSocket(x)

    y.sendall(first)
    try:
        bs.recv_until(delim, timeout=0.0001)
    except Timeout:
        pass
    y.sendall(second)

    assert bs.recv_until(delim) == b'1234\r\n'
    assert bs.recv_size(1) == b'5'
    return


def test_basic_nonblocking():
    delim = b'\n'

    # test with per-call timeout
    x, y = socket.socketpair()
    bs = BufferedSocket(x)

    try:
        bs.recv_until(delim, timeout=0)
    except socket.error as se:
        assert se.errno == errno.EWOULDBLOCK
    y.sendall(delim)
    assert bs.recv_until(delim) == delim

    # test with instance-level default timeout
    x, y = socket.socketpair()
    bs = BufferedSocket(x, timeout=0)

    try:
        bs.recv_until(delim)
    except socket.error as se:
        assert se.errno == errno.EWOULDBLOCK
    y.sendall(delim)
    assert bs.recv_until(delim) == delim

    # test with setblocking(0) on the underlying socket
    x, y = socket.socketpair()
    x.setblocking(0)
    bs = BufferedSocket(x)

    try:
        bs.recv_until(delim)
    except socket.error as se:
        assert se.errno == errno.EWOULDBLOCK
    y.sendall(delim)
    assert bs.recv_until(delim) == delim

    return



def netstring_server(server_socket):
    "A basic netstring server loop, supporting a few operations"
    running = True
    try:
        while running:
            clientsock, addr = server_socket.accept()
            client = NetstringSocket(clientsock)
            while 1:
                request = client.read_ns()
                if request == b'close':
                    clientsock.close()
                    break
                elif request == b'shutdown':
                    running = False
                    break
                elif request == b'reply4k':
                    client.write_ns(b'a' * 4096)
                elif request == b'ping':
                    client.write_ns(b'pong')
                elif request == b'reply128k':
                    client.setmaxsize(128 * 1024)
                    client.write_ns(b'huge' * 32 * 1024)  # 128kb
                    client.setmaxsize(32768)  # back to default
    except Exception as e:
        print(u'netstring_server exiting with error: %r' % e)
        raise
    return


def test_socketutils_netstring():
    """A holistic feature test of BufferedSocket via the NetstringSocket
    wrapper. Runs
    """
    print("running self tests")

    # Set up server
    server_socket = socket.socket()
    server_socket.bind(('127.0.0.1', 0))  # localhost with ephemeral port
    server_socket.listen(100)
    ip, port = server_socket.getsockname()
    start_server = lambda: netstring_server(server_socket)
    threading.Thread(target=start_server).start()

    # set up client
    def client_connect():
        clientsock = socket.create_connection((ip, port))
        client = NetstringSocket(clientsock)
        return client

    # connect, ping-pong
    client = client_connect()
    client.write_ns(b'ping')
    assert client.read_ns() == b'pong'
    s = time.time()
    for i in range(1000):
        client.write_ns(b'ping')
        assert client.read_ns() == b'pong'
    dur = time.time() - s
    print("netstring ping-pong latency", dur, "ms")

    s = time.time()
    for i in range(1000):
        client.write_ns(b'ping')
    resps = []
    for i in range(1000):
        resps.append(client.read_ns())
    e = time.time()
    assert all([r == b'pong' for r in resps])
    assert client.bsock.getrecvbuffer() == b''
    dur = e - s
    print("netstring pipelined ping-pong latency", dur, "ms")

    # tell the server to close the socket and then try a failure case
    client.write_ns(b'close')
    try:
        client.read_ns()
        raise Exception('read from closed socket')
    except ConnectionClosed:
        print("raised ConnectionClosed correctly")

    # test big messages
    client = client_connect()
    client.setmaxsize(128 * 1024)
    client.write_ns(b'reply128k')
    res = client.read_ns()
    assert len(res) == (128 * 1024)
    client.write_ns(b'close')

    # test that read timeouts work
    client = client_connect()
    client.settimeout(0.1)
    try:
        client.read_ns()
        raise Exception('did not timeout')
    except Timeout:
        print("read_ns raised timeout correctly")
    client.write_ns(b'close')

    # test that netstring max sizes work
    client = client_connect()
    client.setmaxsize(2048)
    client.write_ns(b'reply4k')
    try:
        client.read_ns()
        raise Exception('read more than maxsize')
    except NetstringMessageTooLong:
        print("raised MessageTooLong correctly")
    try:
        client.bsock.recv_until(b'b', maxsize=4096)
        raise Exception('recv_until did not raise MessageTooLong')
    except MessageTooLong:
        print("raised MessageTooLong correctly")
    assert client.bsock.recv_size(4097) == b'a' * 4096 + b','
    print('correctly maintained buffer after exception raised')

    # test BufferedSocket read timeouts with recv_until and recv_size
    client.bsock.settimeout(0.01)
    try:
        client.bsock.recv_until(b'a')
        raise Exception('recv_until did not raise Timeout')
    except Timeout:
        print('recv_until correctly raised Timeout')
    try:
        client.bsock.recv_size(1)
        raise Exception('recv_size did not raise Timeout')
    except Timeout:
        print('recv_size correctly raised Timeout')

    client.write_ns(b'shutdown')
    print("all passed")
