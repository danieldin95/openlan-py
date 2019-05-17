'''
Created on Feb 28, 2019

@author: Daniel
'''

import struct 
import socket
import Queue
import logging

from libolan.ethernet import Ethernet
from libolan.tcpmesg import TcpMesg
from libolan.openfib import OpenFibMgr

from ope.tcp.server import TcpServer
from ope.tcp.server import TcpConn
from ope.tcp.server import ERRSBIG
from ope.tcp.server import ERRDNOR

class OpenTcpConn(TcpConn):
    """"""
    HSIZE = 4

    def __init__(self, *args, **kws):
        """"""""
        super(OpenTcpConn, self).__init__(*args, **kws)

    def recvall(self):
        """"""""
        if len(self.rxbuf) < self.HSIZE:
            self.rxbuf += self.recvn(self.HSIZE-len(self.rxbuf))
            if len(self.rxbuf) != self.HSIZE:
                return None

        logging.debug('%s receive: %s', self, repr(self.rxbuf))

        if self.rxbuf[:2] != TcpMesg.MAGIC:
            raise socket.error(ERRDNOR, 'data not right %s'%repr(self.rxbuf))
    
        size = struct.unpack('!H', self.rxbuf[2:4])[0]
        if size > self.maxsize or size <= self.minsize:
            raise socket.error(ERRSBIG, 'too big size %s'%size)

        logging.debug('%s receive: %s', self, size)

        self.rxbuf += self.recvn(size)
        if len(self.rxbuf) != (size + self.HSIZE):
            return None

        self.rxbyte += len(self.rxbuf)

        data = self.rxbuf
        self.rxbuf = ''

        return data

    def sendall(self, d):
        """"""
        self.sendone(d)

        # send remains.
        while not self.txq.empty() and self.txbuf == '':
            self.sendone()

class OpenServer(TcpServer):
    """"""
    def __init__(self, bind_to, **kws):
        """"""
        super(OpenServer, self).__init__(bind_to, **kws)
        self.recvFunc = None

        self.rxq = Queue.Queue()
        self.rxpkt = 0
        self.txpkt = 0
        self.fib = OpenFibMgr()

    def recv(self, conn):
        """
        @param m: TcpConn
        """
        data = super(OpenServer, self).recv(conn)
        if data:
            # forwarding message.
            self.recvMsg(conn, data)

    def recvMsg(self, conn, data):
        """"""
        logging.debug("%s receive %s", conn, repr(data))

        # source learning
        m = TcpMesg.unpack(data)
        self.fib.learn(conn, Ethernet(m.data))

        if self.recvFunc:
            self.recvFunc(conn, m)

        self.rxpkt += 1

    def sendMsg(self, conn, m):
        """
        @param m: TcpMesg's instance  
        """
        self.txpkt += 1

        buf = m.pack()
        logging.debug("%s send %s", conn, repr(buf))

        try:
            if conn.isok():
                conn.sendall(buf)
        except socket.error as e:
            logging.error("%s send %s", conn, e)

    def flood(self, conn, m):
        """"""
        logging.debug("%s broadcast %s", conn, m)
        for toconn in self.listConn():
            if toconn is conn:
                continue

            self.sendMsg(toconn, m)

    def unicast(self, conn, m):
        """"""
        logging.debug("%s unicast %s", conn, m)
        return self.sendMsg(conn, m)

    def forward(self, conn, m):
        """"""
        eth = Ethernet(m.data)
        if Ethernet.isBrocast(eth.dst):
            return self.flood(conn, m)

        entry = self.fib.getEntry(eth.dst)
        if entry is None:
            return self.flood(conn, m)

        if entry.isExpire():
            self.fib.delEntry(entry.ethdst)
            return self.flood(conn, m)

        entry.update()
 
        return self.unicast(entry.conn, m)
