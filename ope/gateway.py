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

from tcpServer import TcpServer, TcpConn, TcpMesg

class OpenServer(TcpServer):
    """"""
    HEADER_SIZE = 4

    def __init__(self, bind_to, **kws):
        """"""
        super(OpenServer, self).__init__(bind_to, **kws)
        self.recvFunc = None
        self.DEBUG = kws.get('DEBUG', False)

        self.rxq = Queue.Queue()

    def recv(self, conn):
        """
        @param m: TcpConn
        """
        d = super(OpenServer, self).recv(conn, self.HEADER_SIZE)
        if len(d) != self.HEADER_SIZE:
            print("receive data for size %s failed"%self.HEADER_SIZE)
            return

        l = struct.unpack('!I', d)[0]

        d = super(OpenServer, self).recv(conn, l)
        if len(d) != l:
            print("receive data for size %s failed"%l)
            return

        self.recvMsg(TcpMesg(conn, d))

    def recvMsg(self, m):
        """
        @param m: TcpMesg
        """
        if self.DEBUG:
            print "%s receive message %s"%(self.__class__.__name__, m)
        if self.recvFunc:
            self.recvFunc(m)

    def sendMsg(self, m):
        """
        @param m: TcpMesg
        """
        buf = struct.pack('!I', len(m.data))
        buf += m.data 
        if self.DEBUG:
            print "%s send message %s"%(self.__class__.__name__, repr(buf))

        try:
            m.conn.fd.send(buf)
        except socket.error as e:
            print "%s send message: %s" %(self.__class__.__name__, e)
            pass

    def flood(self, m):
        """"""
        for conn in self.conns.values():
            if conn is m.conn:
                continue

            self.sendMsg(TcpMesg(conn, m.data))

    def forward(self, m):
        """"""
        if self.DEBUG:
            print "%s send message %s"%(self.__class__.__name__, m)
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
        print "receive signal %s, %s" %(signum, frame)
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

    port    = opts.port
    verbose = opts.verbose

    server = OpenServer(port, DEBUG=verbose)
    sysm = System(Gateway(server))
    sysm.start()

if __name__ == '__main__':
    main()