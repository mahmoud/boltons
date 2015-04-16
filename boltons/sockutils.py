import time
import socket

_UNSET = object()


class BufferedSocket(object):
    def __init__(self, sock, timeout=10, maxbytes=32 * 1024):
        self.sock = sock
        self.sock.settimeout(None)
        self.rbuf = ""
        self.sbuf = []
        self.timeout = timeout
        self.maxbytes = maxbytes

    def settimeout(self, timeout):
        self.timeout = timeout

    def setmaxbytes(self, maxbytes):
        self.maxbytes = maxbytes

    def recv(self, size, flags=0, timeout=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout
        if flags:
            raise ValueError("flags not supported")
        if len(self.rbuf) >= size:
            data, self.rbuf = self.rbuf[:size], self.rbuf[size:]
            return data
        size -= len(self.rbuf)
        self.sock.settimeout(timeout)
        data = self.rbuf + self.sock.recv(size)
        # don't empty buffer till after network communication is complete,
        # to avoid data loss on transient / retry-able errors (e.g. read
        # timeout)
        self.rbuf = ""
        return data

    def peek(self, n, timeout=None):
        'peek n bytes from the socket, but keep them in the buffer'
        if len(self.rbuf) >= n:
            return self.rbuf[:n]
        data = self.recv_all(n, timeout=timeout)
        self.rbuf = data + self.rbuf
        return data

    def recv_until(self, marker, timeout=_UNSET, maxbytes=_UNSET):
        'read off of socket until the marker is found'
        if maxbytes is _UNSET:
            maxbytes = self.maxbytes
        if timeout is _UNSET:
            timeout = self.timeout
        chunks = []
        recvd = 0
        try:
            start = time.time()
            self.sock.settimeout(timeout)
            nxt = self.rbuf or self.sock.recv(32 * 1024)
            while nxt and marker not in nxt:
                chunks.append(nxt)
                recvd += len(nxt)
                if maxbytes is not None and recvd >= maxbytes:
                    raise NotFound(marker, recvd)
                self.sock.settimeout(timeout - (time.time() - start))
                nxt = self.sock.recv(32 * 1024)
            if not nxt:
                raise ConnectionClosed(
                    'connection closed after reading {0} bytes without'
                    ' finding symbol {1}'.format(recvd, marker))
        except socket.timeout:
            self.rbuf = ''.join(chunks)
            raise Timeout(
                timeout, 'read {0} bytes without finding symbol {1}'.format(
                        recvd, marker))
        except:  # in case of error, retain data read so far in buffer
            self.rbuf = ''.join(chunks)
            raise
        val, _, self.rbuf = nxt.partition(marker)
        return ''.join(chunks) + val

    def recv_all(self, size, timeout=_UNSET):
        'read off of socket until size bytes have been read'
        if timeout is _UNSET:
            timeout = self.timeout
        chunks = []
        total_bytes = 0
        try:
            start = time.time()
            self.sock.settimeout(timeout)
            nxt = self.rbuf or self.sock.recv(size)
            while nxt:
                total_bytes += len(nxt)
                if total_bytes >= size:
                    break
                chunks.append(nxt)
                self.sock.settimeout(timeout - (time.time() - start))
                nxt = self.sock.recv(size - total_bytes)
            else:
                raise ConnectionClosed(
                    'connection was closed after reading'
                    ' {0} of {1} bytes'.format(total_bytes, size))
        except socket.timeout:
            self.rbuf = ''.join(chunks)
            raise Timeout(
                timeout, 'read {0} of {1} bytes'.format(total_bytes, size))
        except:  # in case of error, retain data read so far in buffer
            self.rbuf = ''.join(chunks)
            raise
        extra_bytes = total_bytes - size
        if extra_bytes:
            last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
        else:
            last, self.rbuf = nxt, ""
        chunks.append(last)
        return ''.join(chunks)

    def send(self, data, flags=0, timeout=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout
        if flags:
            raise ValueError("flags not supported")
        self.sbuf = [''.join(self.sbuf) + data]
        self.sock.settimeout(timeout)
        start = time.time()
        try:
            while self.sbuf[0]:
                sent = self.sock.send(data)
                self.sbuf[0] = self.sbuf[0][sent:]
                self.sock.settimeout(timeout - (time.time() - start))
        except socket.timeout:
            raise Timeout(
                timeout, "{0} bytes unsent".format(len(self.sbuf[0])))

    sendall = send

    def flush(self):
        self.send('')

    def buffer(self, data):
        self.sbuf.append(data)


class Error(socket.error, Exception):
    pass


class ConnectionClosed(Error):
    pass


class Timeout(socket.timeout, Error):
    def __init__(self, timeout, extra=""):
        if timeout is None:
            super(Timeout, self).__init__('timed out ' + extra)
        else:
            super(Timeout, self).__init__(
                'timed out after {0}ms '.format(timeout * 1e3) + extra)


class NotFound(Error):
    def __init__(self, symbol, bytes_read):
        super(NotFound, self).__init__(
            'read {0} bytes without finding symbol {1}'.format(
                symbol, bytes_read))



class NetstringSocket(object):
    '''
    Reads and writes using the netstring protocol.
    '''
    def __init__(self, sock, timeout=30, maxsize=32 * 1024):
        self.maxlensize = len(str(maxsize)) + 1  # len(str()) == log10
        self.timeout = timeout
        self.maxsize = maxsize
        self.bsock = BufferedSocket(sock)

    def settimeout(self, timeout):
        self.timeout = timeout

    def setmaxsize(self, maxsize):
        self.maxsize = maxsize
        self.maxlensize = len(str(maxsize)) + 1  # len(str()) == log10

    def read_ns(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout
        start = time.time()
        size = int(self.bsock.recv_until(':', self.timeout, self.maxlensize))
        if size > self.maxsize:
            raise NetstringMessageTooLong(size, self.maxsize)
        payload = self.bsock.recv_all(size)
        assert self.bsock.recv(1) == ',', NetstringProtocolError(
            "missing traililng ',' after netstring")
        return payload

    def write_ns(self, payload):
        if len(payload) > self.maxsize:
            raise NetstringMessageTooLong(size, self.maxsize)
        self.bsock.send(str(len(payload)) + ':' + payload + ',')


class NetstringProtocolError(Error):
    pass


class NetstringMessageTooLong(NetstringProtocolError):
    def __init__(self, size, maxsize):
        super(NetstringMessageTooLong, self).__init__(
            'netstring message length {0} > max {1}'.format(size, maxsize))


if __name__ == "__main__":
    def test():
        print "running self tests"
        import thread

        def server():
            running = True
            while running:
                clientsock, addr = serversock.accept()
                client = NetstringSocket(clientsock)
                while 1:
                    request = client.read_ns()
                    if request == 'close':
                        clientsock.close()
                        break
                    if request == 'shutdown':
                        running = False
                        break
                    if request == 'reply4k':
                        client.write_ns('a' * 4096)
                    if request == 'ping':
                        client.write_ns('pong')

        serversock = socket.socket()
        serversock.bind(('127.0.0.1', 0))
        serversock.listen(100)
        ip, port = serversock.getsockname()

        thread.start_new_thread(server, ())

        def client_connect():
            clientsock = socket.create_connection((ip, port))
            client = NetstringSocket(clientsock)
            return client

        client = client_connect()
        client.write_ns('ping')
        assert client.read_ns() == 'pong'
        s = time.time()
        for i in range(1000):
            client.write_ns('ping')
            assert client.read_ns() == 'pong'
        dur = time.time() - s
        print "netstring ping-pong latency", dur, "ms"
        client.write_ns('close')
        try:
            client.read_ns()
            raise Exception('read from closed socket')
        except ConnectionClosed:
            print "raised ConnectionClosed correctly"

        client = client_connect()
        client.settimeout(0.1)
        try:
            client.read_ns()
            raise Exception('did not timeout')
        except Timeout:
            print "read_ns raised timeout correctly"

        client.write_ns('close')

        client = client_connect()
        client.setmaxsize(2048)
        client.write_ns('reply4k')
        try:
            client.read_ns()
            raise Exception('read more than maxsize')
        except NetstringMessageTooLong:
            print "raised MessageTooLong correctly"
        try:
            client.bsock.recv_until('b', maxbytes=4096)
            raise Exception('recv_until did not raise NotFound')
        except NotFound:
            print "raised NotFound correctly"
        assert client.bsock.recv_all(4097) == 'a' * 4096 + ','
        print 'correctly maintained buffer after exception raised'

        client.bsock.settimeout(0.01)
        try:
            client.bsock.recv_until('a')
            raise Exception('recv_until did not raise Timeout')
        except Timeout:
            print 'recv_until correctly raised Timeout'
        try:
            client.bsock.recv_all(1)
            raise Exception('recv_all did not raise Timeout')
        except Timeout:
            print 'recv_all correctly raised Timeout'

        client.write_ns('shutdown')
        print "all passed"

    test()
