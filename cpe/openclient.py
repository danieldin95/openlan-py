'''
Created on Mar 1, 2019

@author: Daniel
'''

import logging
import struct
import socket

from libolan.tcpmesg import TcpMesg

from .tcpclient import TcpClient
from .tcpclient import ERRSBIG
from .tcpclient import ERRDNOR
from .tcpclient import ERRSNOM

class OpenTcpClient(TcpClient):
    """"""
    HSIZE = 4

    def __init__(self, sysid, zone, *args, **kws):
        """"""
        super(OpenTcpClient, self).__init__(*args, **kws)
        self.sysid = sysid
        self.zone  = zone

    def readMsg(self):
        """"""
        try:
            h = self.recvn(self.sock, self.HSIZE)
            if len(h) != self.HSIZE:
                raise socket.error(ERRSNOM, 'receive with size %s(%s)'%(self.HSIZE, len(h)))

            logging.debug('receive: %s', repr(h))

            if h[:2] != TcpMesg.MAGIC:
                raise socket.error(ERRDNOR, 'data not right %s'%repr(h))
            
            l = struct.unpack("!H", h[2:4])[0]
            if l > self.maxsize or l < self.minsize:
                raise socket.error(ERRSBIG, 'too big size %s'%l)
    
            logging.debug('receive size: %s', l)

            d = self.recvn(self.sock, l)
            if len(d) != l:
                raise socket.error(ERRSNOM, 'receive with size %s(%s)'%(l, len(d)))

            return h+d
        except socket.error as e:
            logging.error("receive error: %s", e)
            self.close()

        return None

    def sendMsg(self, data):
        """"""
        m = TcpMesg(self.sysid, self.zone, data=data)
        buf = m.pack()

        self.connect()
        if self.sock is None:
            logging.error("send error: connect to {0}".format(self.addr))
            return 

        logging.debug("send frame to {0}: {1}".format(self.addr, repr(buf)))
        try:
            self.sendn(self.sock, buf)
        except socket.error as e:
            logging.error("send error: %s", e)
            self.close()
