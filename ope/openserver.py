'''
Created on Feb 28, 2019

@author: Daniel
'''

import struct 
import socket
import Queue
import logging
import time

from .tcpserver import TcpServer
from .tcpserver import TcpConn
from .tcpserver import TcpMesg
from .tcpserver import ERRSBIG
from .tcpserver import ERRDNOR

from lib.ethernet import Ethernet
from lib.rwlock import RWLock

class OpenTcpConn(TcpConn):
    """"""
    HSIZE = 4
    MAGIC = '\xff\xff'

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

        if self.rxbuf[:2] != self.MAGIC:
            raise socket.error(ERRDNOR, 'data not right %s'%repr(self.rxbuf))
    
        size = struct.unpack('!H', self.rxbuf[2:4])[0]
        if size > self.maxsize or size <= self.minsize:
            raise socket.error(ERRSBIG, 'too big size %s'%size)

        logging.debug('%s receive: %s', self, size)

        self.rxbuf += self.recvn(size)
        if len(self.rxbuf) != (size + self.HSIZE):
            return None

        self.rxbyte += len(self.rxbuf)

        data = self.rxbuf[self.HSIZE:]
        self.rxbuf = ''

        return data

    def sendall(self, d):
        """"""
        self.sendone(d)

        # send remains.
        while not self.txq.empty() and self.txbuf == '':
            self.sendone()

class OpenFibEntry(object):
    """"""
    def __init__(self, conn, ethdst, **kws):
        """"""
        self.conn = conn
        self.ethdst  = ethdst
        self.createTime = time.time()
        self.updateTime = time.time()
        self.aging = kws.get('aging', 300)

    def update(self, conn=None):
        """"""
        if conn is not None and self.conn is not conn:
            self.conn = conn

        self.updateTime = time.time()

    def upTime(self):
        """"""
        if self.isExpire():
            return 0

        return round(time.time() - self.createTime, 2)

    def isExpire(self):
        """"""
        if (time.time() - self.updateTime > self.aging or
            not self.conn.isok()):
            return True

        return False

    def __str__(self):
        """"""
        return '{0} {1} {2}'.format(Ethernet.addr2Str(self.ethdst), 
                                    self.conn.fd(), self.upTime())

class OpenFibManager(object):
    """"""
    def __init__(self, maxsize=65535):
        """"""
        self.maxsize = maxsize
        self.fib = {}
        self.fibrwl = RWLock()

    def learn(self, conn, eth):
        """"""
        entry = self.getEntry(eth.src)
        if entry is None:
            if len(self.fib) > self.maxsize:
                logging.error('source learning reached max size {0}'
                              .format(self.maxsize))
                # TODO archive fib aging 
                return
            
            entry = OpenFibEntry(conn, eth.src)
            logging.info('source learning {0}'.format(entry))

            with self.fibrwl.writer_lock:
                self.fib[eth.src] = entry
        else:
            entry.update(conn)

    def getEntry(self, ethaddr):
        """"""
        with self.fibrwl.reader_lock:
            fib = self.fib.get(ethaddr)

        return fib

    def delEntry(self, ethaddr):
        """"""
        with self.fibrwl.writer_lock:
            if ethaddr in self.fib:
                self.fib.pop(ethaddr)

    def listEntry(self):
        """"""
        with self.fibrwl.reader_lock:
            for fib in self.fib.values():
                yield fib

class OpenServer(TcpServer):
    """"""
    MAGIC = '\xff\xff'

    def __init__(self, bind_to, **kws):
        """"""
        super(OpenServer, self).__init__(bind_to, **kws)
        self.recvFunc = None

        self.rxq = Queue.Queue()
        self.rxpkt = 0
        self.txpkt = 0
        self.fib = OpenFibManager()

    def recv(self, conn):
        """
        @param m: TcpConn
        """
        data = super(OpenServer, self).recv(conn)
        if data:
            # forwarding message.
            self.recvMsg(TcpMesg(conn, data))

    def recvMsg(self, m):
        """
        @param m: TcpMesg
        """
        logging.debug("%s receive %s", self.__class__.__name__, m)

        # source learning
        self.fib.learn(m.conn, Ethernet(m.data))

        if self.recvFunc:
            self.recvFunc(m)

        self.rxpkt += 1

    def sendMsg(self, m):
        """
        @param m: TcpMesg
        """
        self.txpkt += 1

        buf = self.MAGIC
        buf += struct.pack('!H', len(m.data))
        buf += m.data 
        logging.debug("%s send %s", m.conn, repr(buf))

        try:
            if m.conn.isok():
                m.conn.sendall(buf)
        except socket.error as e:
            logging.error("%s send %s", m.conn, e)
            pass

    def flood(self, m):
        """"""
        logging.debug("%s broadcast %s", self.__class__.__name__, m)
        for conn in self.listConn():
            if conn is m.conn:
                continue

            self.sendMsg(TcpMesg(conn, m.data))

    def unicast(self, conn, m):
        """"""
        logging.debug("%s unicast %s", self.__class__.__name__, m)
        return self.sendMsg(TcpMesg(conn, m.data))

    def forward(self, m):
        """"""
        eth = Ethernet(m.data)
        if Ethernet.isBrocast(eth.dst):
            return self.flood(m)

        entry = self.fib.getEntry(eth.dst)
        if entry is None:
            return self.flood(m)

        if entry.isExpire():
            self.fib.delEntry(entry.ethdst)
            return self.flood(m)

        entry.update()
 
        return self.unicast(entry.conn, m)
