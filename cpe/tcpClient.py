'''
Created on Feb 16, 2019

@author: info
'''

import socket
import struct
import logging

class TcpClient(object):
    """"""
    HEADER_SIZE = 4

    def __init__(self, server, port=10001, **kws):
        """"""
        self.server = server
        self.port = port

        self.sock = None

    def connect(self):
        """"""
        if self.sock is not None:
            return

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.server, self.port))
        except socket.error:
            self.sock = None

    def recvn(self, sock, n):
        """"""
        buf = ''
        left = n
        while left > 0:
            d = sock.recv(left)
            if len(d) == 0:
                raise socket.error(90002, 'receive zero message')

            left -= len(d)
            buf += d

        return buf

    def sendn(self, sock, d):
        """"""
        n = 0
        while n < len(d):
            d = d[n:]
            n = sock.send(d)
            if n == 0:
                raise socket.error(90002, 'send zero message')

    def readMsg(self):
        """
        0    7    15   23    31
        +-+-+-+-+-+-+-+-+-+-+-+
        +        Length       +
        +-+-+-+-+-+-+-+-+-+-+-+
        +        Payload      +
        +-+-+-+-+-+-+-+-+-+-+-+
        """
        try:
            l = self.HEADER_SIZE
            d = self.recvn(self.sock, l)
            if len(d) != self.HEADER_SIZE:
                raise socket.error(90001, 'receive with size %s(%s)'%(l, len(d)))

            logging.debug('receive: %s', repr(d))

            l = struct.unpack("!I", d)[0]
            logging.debug('receive size: %s', l)

            d = self.recvn(self.sock, l)
            if len(d) != l:
                raise socket.error(90001, 'receive with size %s(%s)'%(l, len(d)))

            return d
        except socket.error as e:
            logging.error("receive error: %s", e)
            self.close()

        return None

    def close(self):
        """"""
        if self.sock is None:
            return

        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except socket.error as e:
            logging.error('%s', e)

        self.sock = None

    def sendMsg(self, data):
        """"""
        buf = struct.pack('!I', len(data))
        buf += data

        self.connect()
        if self.sock is None:
            logging.error("send error: connect to (%s:%s)", self.server, self.port)
            return 

        logging.debug("send frame to %s: %s", self.server, repr(buf))
        try:
            self.sendn(self.sock, buf)
        except socket.error as e:
            logging.error("send error: %s", e)
            self.close()

    def isok(self):
        """"""
        return self.sock is not None
