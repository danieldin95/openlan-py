#!/usr/bin/env python

'''
Created on Feb 16, 2019

@author: info
'''

import optparse
import struct 
import socket
import os
import signal
import Queue
import logging

from tcpServer import TcpServer
from tcpServer import TcpConn
from tcpServer import TcpMesg
from tcpServer import ERRSBIG
from tcpServer import ERRDNOR
from lib.log import basicConfig

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

    def recv(self, conn):
        """
        @param m: TcpConn
        """
        data = super(OpenServer, self).recv(conn)
        if data:
            self.recvMsg(TcpMesg(conn, data))

    def recvMsg(self, m):
        """
        @param m: TcpMesg
        """
        logging.debug("%s receive %s", self.__class__.__name__, m)
        if self.recvFunc:
            self.recvFunc(m)

        self.rxpkt +=1

    def sendMsg(self, m):
        """
        @param m: TcpMesg
        """
        self.txpkt +=1

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
        for conn in self.conns.values():
            if conn is m.conn:
                continue

            self.sendMsg(TcpMesg(conn, m.data))

    def forward(self, m):
        """"""
        #logging.debug("%s send %s", self.__class__.__name__, m)
        # TODO unicast mesg.
        self.flood(m) 

class Gateway(object):
    """"""
    def __init__(self, server):
        """"""
        self.server = server
        self.server.recvFunc  = self.forward
        
    def loop(self):
        """"""
        self.server.loop()

    def forward(self, m):
        """"""
        self.server.forward(m)

class System(object):
    """"""
    pidfile='/var/run/ope.pid'

    def __init__(self, gateway):
        """"""
        signal.signal(signal.SIGINT, self.signal)
        signal.signal(signal.SIGTERM, self.signal)

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
    opt = optparse.OptionParser()
    opt.add_option('-v', '--verbose', action="store_true", 
                   dest='verbose', default=False, help='enable verbose')
    opt.add_option('-p', '--port', action='store', 
                   dest='port', default=10001, help='the port of ope connect to')

    opts, _ = opt.parse_args()

    port    = int(opts.port)
    verbose = opts.verbose

    if verbose:
        basicConfig('../gateway.log', logging.DEBUG)
    else:
        basicConfig('../gateway.log', logging.INFO)

    server = OpenServer(port, tcpConn=OpenTcpConn)
    sysm = System(Gateway(server))
    sysm.start()

if __name__ == '__main__':
    main()
