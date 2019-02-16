'''
Created on Feb 16, 2019

@author: info
'''

import socket
import struct

class TcpClient(object):
    """"""
    HEADER_SIZE = 4

    def __init__(self, server, port=10001):
        """"""
        self.server = server
        self.port = port
        
        self.s = None

    def connect(self):
        """"""
        if self.s is not None:
            return
    
        try:
            self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.s.connect((self.server, self.port))
        except socket.error:
            self.s = None

    def readMsg(self):
        """
        0    7    15   23    31
        +-+-+-+-+-+-+-+-+-+-+-+
        +        Length       +
        +-+-+-+-+-+-+-+-+-+-+-+
        +        Payload      +
        +-+-+-+-+-+-+-+-+-+-+-+
        """
        d = self.s.recv(self.HEADER_SIZE)
        if len(d) != self.HEADER_SIZE:
            raise ValueError('receive message header with size %s'%self.HEADER_SIZE)

        l = struct.unpack("!I", d)[0]

        d = self.s.recv(l)
        if len(d) != l:
            raise ValueError('receive message header with size %s'%l)

        return d
    
    def sendMsg(self, data):
        """"""
        buf = struct.pack('!I', len(data))
        buf += data

        self.connect()
        if self.s is None:
            print "send message error: connect gateway(%s:%s) failed"%(self.server, self.port)
            return 

        print "send frame to %s: %s" %(self.server, repr(buf))
        try:
            self.s.send(buf)
        except socket.error as e:
            print "send message error: %s" % e
            self.s = None