#!/usr/bin/env python

'''
Created on Feb 16, 2019

@author: info
'''

import sys
import struct 

from tcpServer import TcpServer, TcpConn, TcpMesg

class OpenServer(TcpServer):
    """"""
    HEADER_SIZE = 4

    def __init__(self, bind_to):
        """"""
        super(OpenServer, self).__init__(bind_to)
        self.recvFunc = None

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
        print "%s receive message %s"%(self.__class__.__name__, m)
        if self.recvFunc:
            self.recvFunc(m)

    def sendMsg(self, m):
        """
        @param m: TcpMesg
        """
        print "%s send message %s"%(self.__class__.__name__, m)
        # TODO unicast mesg.
        self.floodMsg(m) 

    def floodMsg(self, m):
        """"""
        for conn in self.connns.values():
            conn.fd.send(m.data)

class Gateway(object):
    """"""
    def __init__(self, server):
        """"""
        self.server = server
        
    def loop(self):
        """"""
        self.server.loop()

def main():
    """"""
    if len (sys.argv) == 1:
        port = 10001
    elif len(sys.argv) == 2:
        port = int(sys.argv[1])
    else:
        print 'usage: gateway <port>'
        return

    server = OpenServer(port)
    gw = Gateway(server)
    gw.loop()

if __name__ == '__main__':
    main()