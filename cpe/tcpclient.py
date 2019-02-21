'''
Created on Feb 16, 2019

@author: Daniel
'''

import socket
import logging

ERRZMSG = 9000 # zero message
ERRSBIG = 9001 # size big
ERRSNOM = 9002 # size not match
ERRDNOR = 9003 # data not right

class TcpClient(object):
    """"""
    def __init__(self, server, port=5551, **kws):
        """"""
        self.server = server
        self.port = port
        self.maxsize = kws.get('maxsize', 1514)
        self.minsize = kws.get('minsize', 15)

        self.sock = None

    def connect(self):
        """"""
        if self.sock is not None:
            return

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            logging.info("connecting to {0}:{1}".format(self.server, self.port))
            self.sock.connect((self.server, self.port))
        except socket.error as e:
            logging.error('connecting {0}'.format(e))
            self.sock = None

    def recvn(self, sock, n):
        """"""
        buf = ''
        left = n
        while left > 0:
            d = sock.recv(left)
            if len(d) == 0:
                raise socket.error(ERRZMSG, 'receive zero message')

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
                raise socket.error(ERRZMSG, 'send zero message')

    def close(self):
        """"""
        if self.sock is None:
            return

        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except socket.error as e:
            logging.error('%s', e)

        self.sock = None

    def isok(self):
        """"""
        return self.sock is not None
