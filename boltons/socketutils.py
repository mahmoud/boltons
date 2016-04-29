# -*- coding: utf-8 -*-
"""At its heart, Python can be viewed as an extension of the C
programming language. Springing from the most popular systems
programming language has made Python itself a great language for
systems programming. One key to success in this domain is Python's
very serviceable :mod:`socket` module and its :class:`socket.socket`
type.

The ``socketutils`` module provides natural next steps to the ``socket``
builtin: straightforward, tested building blocks for higher-level
protocols.

The :class:`BufferedSocket` wraps an ordinary socket, but provides a
layer of buffering for both sending and receiving. This facilitates
parsing messages from streams, which is necessary for virtually all
protocols on TCP and UDS sockets in ``SOCK_STREAM`` mode. The
Bufferedsocket enables receiving until the next relevant token, or up
to a certain size. It also provides size limiting, as well as timeouts
that are compatible with multiple concurrency paradigms.

This module also provides the :class:`NetstringSocket`, a pure-Python
implementation of the Netstring protocol, built on the
:class:`BufferedSocket`.

Special thanks to `Kurt Rose`_ for his original authorship and all his
contributions on this module.

.. _Kurt Rose: https://github.com/doublereedkurt

"""


import time
import socket

try:
    from threading import RLock
except Exception:
    class RLock(object):
        'Dummy reentrant lock for builds without threads'
        def __enter__(self):
            pass

        def __exit__(self, exctype, excinst, exctb):
            pass


try:
    from typeutils import make_sentinel
    _UNSET = make_sentinel(var_name='_UNSET')
except ImportError:
    _UNSET = object()


DEFAULT_TIMEOUT = 10  # 10 seconds
DEFAULT_MAXSIZE = 32 * 1024  # 32kb
_RECV_LARGE_MAXSIZE = 1024 ** 5  # 1PB


class BufferedSocket(object):
    """Mainly provides recv_until and recv_size. recv, send, sendall, and
    peek all function as similarly as possible to the built-in socket
    API.

    This type has been tested against both the built-in socket type as
    well as those from gevent and eventlet. It also features support
    for sockets with timeouts set to 0 (aka nonblocking), provided the
    caller is prepared to handle the EWOULDBLOCK exceptions.

    Args:
        sock (socket): The connected socket to be wrapped.
        timeout (float): The default timeout for sends and recvs, in
            seconds. Set to ``None`` for no timeout, and 0 for
            nonblocking. Defaults to *sock*'s own timeout if already set,
            and 10 seconds otherwise.
        maxsize (int): The default maximum number of bytes to be received
            into the buffer before it is considered full and raises an
            exception. Defaults to 32 kilobytes.
        recvsize (int): The number of bytes to recv for every
            lower-level :meth:`socket.recv` call. Defaults to *maxsize*.

    *timeout* and *maxsize* can both be overridden on individual socket
    operations.

    All ``recv`` methods return bytestrings (:class:`bytes`) and can
    raise :exc:`socket.error`. :exc:`Timeout`,
    :exc:`ConnectionClosed`, and :exc:`MessageTooLong` all inherit
    from :exc:`socket.error` and exist to provide better error
    messages. Received bytes are always buffered, even if an exception
    is raised. Use :meth:`BufferedSocket.getrecvbuffer` to retrieve
    partial recvs.

    BufferedSocket does not replace the built-in socket by any
    means. While the overlapping parts of the API are kept parallel to
    the built-in :class:`socket.socket`, BufferedSocket does not
    inherit from socket, and most socket functionality is only
    available on the underlying socket. :meth:`socket.getpeername`,
    :meth:`socket.getsockname`, :meth:`socket.fileno`, and others are
    only available on the underlying socket that is wrapped. Use the
    ``BufferedSocket.sock`` attribute to access it. See the examples
    for more information on how to use BufferedSockets with built-in
    sockets.

    The BufferedSocket is threadsafe, but consider the semantics of
    your protocol before accessing a single socket from multiple
    threads.
    """
    def __init__(self, sock, timeout=_UNSET,
                 maxsize=DEFAULT_MAXSIZE, recvsize=_UNSET):
        self.sock = sock
        self.rbuf = b''
        self.sbuf = []
        self.maxsize = int(maxsize)

        if timeout is _UNSET:
            if self.sock.gettimeout() is None:
                self.timeout = DEFAULT_TIMEOUT
            else:
                self.timeout = self.sock.gettimeout()
        else:
            if timeout is None:
                self.timeout = timeout
            else:
                self.timeout = float(timeout)

        if recvsize is _UNSET:
            self._recvsize = self.maxsize
        else:
            self._recvsize = int(recvsize)

        self.send_lock = RLock()
        self.recv_lock = RLock()

    def settimeout(self, timeout):
        "Set the default *timeout* for future operations, in seconds."
        self.timeout = timeout

    def setmaxsize(self, maxsize):
        """Set the default maximum buffer size *maxsize* for future
        operations, in bytes. Does not truncate the current buffer.
        """
        self.maxsize = maxsize

    def getrecvbuffer(self):
        "Returns the receive buffer bytestring (rbuf)."
        with self.recv_lock:
            return self.rbuf

    def getsendbuffer(self):
        "Returns a copy of the send buffer list."
        with self.send_lock:
            return list(self.sbuf)

    def recv(self, size, flags=0, timeout=_UNSET):
        """Returns **up to** *size* bytes, using the internal buffer before
        performing a single :meth:`socket.recv` operation.

        Args:
            size (int): The maximum number of bytes to receive.
            flags (int): Kept for API compatibility with sockets. Only
                the default, ``0``, is valid.
            timeout (float): The timeout for this operation. Can be
                ``0`` for nonblocking and ``None`` for no
                timeout. Defaults to the value set in the constructor
                of BufferedSocket.

        If the operation does not complete in *timeout* seconds, a
        :exc:`Timeout` is raised. Much like the built-in
        :class:`socket.socket`, if this method returns an empty string,
        then the socket is closed and recv buffer is empty. Further
        calls to recv will raise :exc:`socket.error`.

        """
        with self.recv_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported: %r" % flags)
            if len(self.rbuf) >= size:
                data, self.rbuf = self.rbuf[:size], self.rbuf[size:]
                return data
            if self.rbuf:
                ret, self.rbuf = self.rbuf, b''
                return ret
            self.sock.settimeout(timeout)
            try:
                data = self.sock.recv(self._recvsize)
            except socket.timeout:
                raise Timeout(timeout)  # check the rbuf attr for more
            if len(data) > size:
                data, self.rbuf = data[:size], data[size:]
        return data

    def peek(self, size, timeout=_UNSET):
        """Returns *size* bytes from the socket and/or internal buffer. Bytes
        are kept in the buffer.

        Args:
            size (int): The exact number of bytes to peek at
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        """
        with self.recv_lock:
            if len(self.rbuf) >= size:
                return self.rbuf[:size]
            data = self.recv_size(size, timeout=timeout)
            self.rbuf = data + self.rbuf
        return data

    def recv_close(self, timeout=_UNSET, maxsize=_UNSET):
        """Receive until the connection is closed, up to *maxsize* bytes. If
        more than *maxsize* bytes are received, raises :exc:`MessageTooLong`.
        """
        with self.recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            try:
                recvd = self.recv_size(maxsize + 1, timeout)
            except ConnectionClosed:
                ret, self.rbuf = self.rbuf, b''
            else:
                # put extra received bytes (now in rbuf) after recvd
                self.rbuf = recvd + self.rbuf
                size_read = min(maxsize, len(self.rbuf))
                raise MessageTooLong(size_read)  # check receive buffer
        return ret

    def recv_until(self, delimiter, timeout=_UNSET, maxsize=_UNSET):
        """Receive until *delimiter* is found, *timeout* is exceeded, or internal
        buffer reaches *maxsize*.

        Args:
            delimiter (bytes): The byte or bytestring to be searched for
                in the socket stream.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.
            maxsize (int): The maximum size for the internal buffer.
                Defaults to the value set in the constructor.
        """
        with self.recv_lock:
            if maxsize is _UNSET:
                maxsize = self.maxsize
            if maxsize is None:
                maxsize = _RECV_LARGE_MAXSIZE
            if timeout is _UNSET:
                timeout = self.timeout

            sock = self.sock
            recvd = bytearray(self.rbuf)
            start = time.time()
            find_offset_start = 0  # becomes a negative index below

            if not timeout:  # covers None (no timeout) and 0 (nonblocking)
                sock.settimeout(timeout)
            try:
                while 1:
                    offset = recvd.find(delimiter, find_offset_start, maxsize)
                    if offset != -1:  # str.find returns -1 when no match found
                        offset += len(delimiter)  # include delimiter in return
                        break
                    elif len(recvd) > maxsize:
                        raise MessageTooLong(maxsize, delimiter)  # see rbuf
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        sock.settimeout(cur_timeout)
                    nxt = sock.recv(self._recvsize)
                    if not nxt:
                        args = (len(recvd), delimiter)
                        msg = ('connection closed after reading %s bytes'
                               ' without finding symbol: %r' % args)
                        raise ConnectionClosed(msg)  # check the recv buffer
                    recvd.extend(nxt)
                    find_offset_start = -len(nxt) - len(delimiter) + 1
            except socket.timeout:
                self.rbuf = bytes(recvd)
                msg = ('read %s bytes without finding delimiter: %r'
                       % (len(recvd), delimiter))
                raise Timeout(timeout, msg)  # check the recv buffer
            except Exception:
                self.rbuf = bytes(recvd)
                raise
            val, self.rbuf = bytes(recvd[:offset]), bytes(recvd[offset:])
        return val

    def recv_size(self, size, timeout=_UNSET):
        """Read off of the internal buffer, then off the socket, until exactly
        *size* bytes have been read.

        Args:
            size (int): number of bytes to read before returning.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        If the appropriate number of bytes cannot be fetched from the
        buffer and socket before *timeout* expires, then a
        :exc:`Timeout` will be raised. If the connection is closed, a
        :exc:`ConnectionClosed` will be raised.
        """
        with self.recv_lock:
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
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
                    nxt = self.sock.recv(self._recvsize)
                else:
                    msg = ('connection closed after reading %s of %s requested'
                           ' bytes' % (total_bytes, size))
                    raise ConnectionClosed(msg)  # check recv buffer
            except socket.timeout:
                self.rbuf = b''.join(chunks)
                msg = 'read %s of %s bytes' % (total_bytes, size)
                raise Timeout(timeout, msg)  # check recv buffer
            except Exception:
                # received data is still buffered in the case of errors
                self.rbuf = b''.join(chunks)
                raise
            extra_bytes = total_bytes - size
            if extra_bytes:
                last, self.rbuf = nxt[:-extra_bytes], nxt[-extra_bytes:]
            else:
                last, self.rbuf = nxt, b''
            chunks.append(last)
        return b''.join(chunks)

    def send(self, data, flags=0, timeout=_UNSET):
        """Send the contents of the internal send buffer, as well as *data*,
        to the receiving end of the connection. Returns the total
        number of bytes sent. If no exception is raised, all of *data* was
        sent and the internal send buffer is empty.

        Args:
            data (bytes): The bytes to send.
            flags (int): Kept for API compatibility with sockets. Only
                the default 0 is valid.
            timeout (float): The timeout for this operation. Can be 0 for
                nonblocking and None for no timeout. Defaults to the value
                set in the constructor of BufferedSocket.

        Will raise :exc:`Timeout` if the send operation fails to
        complete before *timeout*. In the event of an exception, use
        :meth:`BufferedSocket.getsendbuffer` to see which data was
        unsent.

        """
        with self.send_lock:
            if timeout is _UNSET:
                timeout = self.timeout
            if flags:
                raise ValueError("non-zero flags not supported")
            sbuf = self.sbuf
            sbuf.append(data)
            if len(sbuf) > 1:
                sbuf[:] = [b''.join([s for s in sbuf if s])]
            self.sock.settimeout(timeout)
            start, total_sent = time.time(), 0
            try:
                while sbuf[0]:
                    sent = self.sock.send(sbuf[0])
                    total_sent += sent
                    sbuf[0] = sbuf[0][sent:]
                    if timeout:
                        cur_timeout = timeout - (time.time() - start)
                        if cur_timeout <= 0.0:
                            raise socket.timeout()
                        self.sock.settimeout(cur_timeout)
            except socket.timeout:
                raise Timeout(timeout, '%s bytes unsent' % len(sbuf[0]))
        return total_sent

    def sendall(self, data, flags=0, timeout=_UNSET):
        """An passthrough to :meth:`~BufferedSocket.send`, retained for
        parallelism to the :class:`socket.socket` API.
        """
        return self.send(data, flags, timeout)

    def flush(self):
        "Send the contents of the internal send buffer."
        with self.send_lock:
            self.send(b'')
        return

    def buffer(self, data):
        "Buffer *data* bytes for the next send operation."
        with self.send_lock:
            self.sbuf.append(data)
        return


class Error(socket.error):
    """A subclass of :exc:`socket.error` from which all other
    ``socketutils`` exceptions inherit.

    When using :class:`BufferedSocket` and other ``socketutils``
    types, generally you want to catch one of the specific exception
    types below, or :exc:`socket.error`.
    """
    pass


class ConnectionClosed(Error):
    pass


class MessageTooLong(Error):
    """Raised from :meth:`BufferedSocket.recv_until` and
    :meth:`BufferedSocket.recv_closed` when more than *maxsize* bytes are
    read without encountering the delimiter or a closed connection,
    respectively.
    """
    def __init__(self, bytes_read=None, delimiter=None):
        msg = 'message exceeded maximum size'
        if bytes_read is not None:
            msg += '. %s bytes read' % (bytes_read,)
        if delimiter is not None:
            msg += '. Delimiter not found: %r' % (delimiter,)
        super(MessageTooLong, self).__init__(msg)


class Timeout(socket.timeout, Error):
    def __init__(self, timeout, extra=""):
        msg = 'socket operation timed out'
        if timeout is not None:
            msg += ' after %sms' % (timeout * 1000)
        if extra:
            msg += '.' + extra
        super(Timeout, self).__init__(msg)


class NetstringSocket(object):
    """
    Reads and writes using the netstring protocol.

    More info: https://en.wikipedia.org/wiki/Netstring
    Even more info: http://cr.yp.to/proto/netstrings.txt
    """
    def __init__(self, sock, timeout=DEFAULT_TIMEOUT, maxsize=DEFAULT_MAXSIZE):
        self.bsock = BufferedSocket(sock)
        self.timeout = timeout
        self.maxsize = maxsize
        self._msgsize_maxsize = len(str(maxsize)) + 1  # len(str()) == log10

    def fileno(self):
        return self.bsock.fileno()

    def settimeout(self, timeout):
        self.timeout = timeout

    def setmaxsize(self, maxsize):
        self.maxsize = maxsize
        self._msgsize_maxsize = len(str(maxsize)) + 1  # len(str()) == log10

    def read_ns(self, timeout=_UNSET, maxsize=_UNSET):
        if timeout is _UNSET:
            timeout = self.timeout

        size_prefix = self.bsock.recv_until(b':',
                                            timeout=self.timeout,
                                            maxsize=self._msgsize_maxsize)

        size_bytes, sep, _ = size_prefix.partition(b':')

        if not sep:
            raise NetstringInvalidSize('netstring messages must start with'
                                       ' "size:", not %r' % size_prefix)
        try:
            size = int(size_bytes)
        except ValueError:
            raise NetstringInvalidSize('netstring message size must be valid'
                                       ' integer, not %r' % size_bytes)

        if size > self.maxsize:
            raise NetstringMessageTooLong(size, self.maxsize)
        payload = self.bsock.recv_size(size)
        if self.bsock.recv(1) != b',':
            raise NetstringProtocolError("expected trailing ',' after message")

        return payload

    def write_ns(self, payload):
        size = len(payload)
        if size > self.maxsize:
            raise NetstringMessageTooLong(size, self.maxsize)
        data = str(size).encode('ascii') + b':' + payload + b','
        self.bsock.send(data)


class NetstringProtocolError(Error):
    pass


class NetstringInvalidSize(NetstringProtocolError):
    def __init__(self, msg):
        super(NetstringMessageTooLong, self).__init__(msg)


class NetstringMessageTooLong(NetstringProtocolError):
    def __init__(self, size, maxsize):
        msg = ('netstring message length exceeds configured maxsize: %s > %s'
               % (size, maxsize))
        super(NetstringMessageTooLong, self).__init__(msg)
