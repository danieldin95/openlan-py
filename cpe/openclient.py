'''
Created on Mar 1, 2019

@author: info
'''

import logging
import struct
import socket

from .tcp_client import TcpClient
from .tcp_client import ERRSBIG
from .tcp_client import ERRDNOR
from .tcp_client import ERRSNOM

class OpenTcpClient(TcpClient):
    """"""
    HSIZE = 4
    MAGIC = '\xff\xff'

    def __init__(self, *args, **kws):
        """"""
        super(OpenTcpClient, self).__init__(*args, **kws)

    def readMsg(self):
        """"""
        try:
            d = self.recvn(self.sock, self.HSIZE)
            if len(d) != self.HSIZE:
                raise socket.error(ERRSNOM, 'receive with size %s(%s)'%(self.HSIZE, len(d)))

            logging.debug('receive: %s', repr(d))

            if d[:2] != self.MAGIC:
                raise socket.error(ERRDNOR, 'data not right %s'%repr(d))
            
            l = struct.unpack("!H", d[2:4])[0]
            if l > self.maxsize or l < self.minsize:
                raise socket.error(ERRSBIG, 'too big size %s'%l)
    
            logging.debug('receive size: %s', l)

            d = self.recvn(self.sock, l)
            if len(d) != l:
                raise socket.error(ERRSNOM, 'receive with size %s(%s)'%(l, len(d)))

            return d
        except socket.error as e:
            logging.error("receive error: %s", e)
            self.close()

        return None

    def sendMsg(self, data):
        """"""
        buf = self.MAGIC
        buf += struct.pack('!H', len(data))
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