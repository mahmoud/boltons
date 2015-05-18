# -*- coding: utf-8 -*-

import time
import socket
import threading
from boltons.socketutils import (NetstringSocket,
                                 ConnectionClosed,
                                 NetstringMessageTooLong,
                                 NotFound,
                                 Timeout)


def netstring_server(server_socket):
    "A basic netstring server loop, supporting a few operations"
    running = True
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

    # tell the server to close the socket and then try a failure case
    client.write_ns(b'close')
    try:
        client.read_ns()
        raise Exception('read from closed socket')
    except ConnectionClosed:
        print("raised ConnectionClosed correctly")

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
        client.bsock.recv_until(b'b', maxbytes=4096)
        raise Exception('recv_until did not raise NotFound')
    except NotFound:
        print("raised NotFound correctly")
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
