#!/usr/bin/env python

'''
Created on Feb 16, 2019

@author: info
'''

import struct 
import socket
import os
import signal
import Queue
import logging
import time

from tcp_server import TcpServer
from tcp_server import TcpConn
from tcp_server import TcpMesg
from tcp_server import ERRSBIG
from tcp_server import ERRDNOR

from lib.log import basicConfig
from lib.ethernet import Ethernet

from options import addOptions
from options import parseOptions
from __builtin__ import False

class OpenTcpConn(TcpConn):
    """"""
    HSIZE = 4
    MAGIC = '\xff\xff'

    def __init__(self, *args, **kws):
        """"""""
        super(OpenTcpConn, self).__init__(*args, **kws)
        self.rxpkt  = 0
        self.txpkt  = 0
        self.txdrop = 0
        self.rxbuf  = ''

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

    def sourceLearn(self, conn, eth):
        """"""
        entry = self.fib.get(eth.src)
        if entry is None:
            if len(self.fib) > self.maxsize:
                logging.error('source learning reached max size {0}'
                              .format(self.maxsize))
            # TODO archive fib aging 
            entry = OpenFibEntry(conn, eth.src)
            logging.info('source learning {0}'.format(entry))

            self.fib[eth.src] = entry
        else:
            entry.update(conn)

    def entryFind(self, ethaddr):
        """"""
        return self.fib.get(ethaddr)

    def entryRemove(self, ethaddr):
        """"""
        if ethaddr in self.fib:
            self.fib.pop(ethaddr)

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
        self.fib.sourceLearn(m.conn, Ethernet(m.data))

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
        logging.debug("%s send %s", self.__class__.__name__, repr(buf))

        try:
            if m.conn.isok():
                m.conn.sendall(buf)
        except socket.error as e:
            logging.error("%s send %s", self.__class__.__name__, e)
            pass

    def flood(self, m):
        """"""
        logging.debug("%s broadcast %s", self.__class__.__name__, m)
        for conn in self.conns.values():
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
            self.flood(m)
            return
    
        entry = self.fib.entryFind(eth.dst)
        if entry is None:
            return self.flood(m)

        if entry.isExpire():
            self.fib.entryRemove(entry.ethdst)
            return self.flood(m)

        entry.update()
        return self.unicast(entry.conn, m)

class Gateway(object):
    """"""
    servers = {}

    def __init__(self, server):
        """"""
        self.server = server

        if Gateway.servers.get(server.key()) is None:
            Gateway.servers[server.key()] = server

        self.server.recvFunc  = self.forward

    def loop(self):
        """"""
        self.server.loop()

    def forward(self, m):
        """"""
        self.server.forward(m)

    @classmethod
    def getServer(cls, key=None):
        """"""
        if key is None:
            if len(cls.servers) > 0: 
                return cls.servers.values()[0] 

            return None

        return cls.servers.get(key)

class System(object):
    """"""
    pidfile='/var/run/ope.pid'

    def __init__(self, gateway):
        """"""
        signal.signal(signal.SIGINT, self.signal)
        signal.signal(signal.SIGTERM, self.signal)
        signal.signal(signal.SIGKILL, self.signal)
        signal.signal(signal.SIGABRT, self.signal)

        self.gateway = gateway

    def savepid(self):
        """"""
        with open(self.pidfile, 'w') as fp:
            fp.write(str(os.getpid()))

    def exit(self):
        """"""
        self.gateway.server.close()
        
    def signal(self, signum, frame):
        """"""
        logging.info("receive signal %s, %s", signum, frame)
        self.exit()

    def start(self):
        """"""
        self.savepid()
        self.gateway.loop()

def main():
    """"""
    addOptions()
    opts, _ = parseOptions()

    port    = int(opts.port)
    verbose = opts.verbose

    if verbose:
        basicConfig(opts.log, logging.DEBUG)
    else:
        basicConfig(opts.log, logging.INFO)

    server = OpenServer(port, tcpConn=OpenTcpConn)
    sysm = System(Gateway(server))
    sysm.start()

if __name__ == '__main__':
    main()
