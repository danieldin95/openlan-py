#!/usr/bin/env python

'''
Created on Feb 16, 2019

@author: info
'''

import commands
import select
import os
import signal
import optparse
import sys
import logging
import struct
import socket

from tcpClient import TcpClient
from tcpClient import ERRSBIG
from tcpClient import ERRDNOR
from tcpClient import ERRSNOM

from lib.log import basicConfig

def addlibdy():
    """"""
    libdir = os.path.dirname(__file__)+'/../lib-dynload'
    sys.path.append(libdir)

addlibdy()

from pytun import TunTapDevice
from pytun import IFF_TAP
from pytun import IFF_NO_PI

"""
    0       7        15       23       31
    +-+-+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+
    +       0xFFFF   |      Length     +
    +-+-+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+
    +              Payload             +
    +-+-+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+
"""
        
class OpenTcpClient(TcpClient):
    """"""
    HSIZE = 4

    def __init__(self, *args, **kws):
        """"""
        super(OpenTcpClient, self).__init__(*args, **kws)

    def readMsg(self):
        """
        0    7    15   23    31
        +-+-+-+-+-+-+-+-+-+-+-+
        +  0xffFF  |  Length  +
        +-+-+-+-+-+-+-+-+-+-+-+
        +        Payload      +
        +-+-+-+-+-+-+-+-+-+-+-+
        """
        try:
            l = self.HSIZE
            d = self.recvn(self.sock, l)
            if len(d) != self.HSIZE:
                raise socket.error(ERRSNOM, 'receive with size %s(%s)'%(l, len(d)))

            logging.debug('receive: %s', repr(d))

            l = struct.unpack("!I", d)[0]
            if l & 0xffFF0000 != 0xffFF0000:
                raise socket.error(ERRDNOR, 'data not right %x'%l)
            
            l &= 0xffFF
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
        buf = struct.pack('!I', len(data) | 0xffff0000)
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

class Bridge(object):
    """"""
    ETHLEN = 14
    
    def __init__(self, gateway, port=10001, **kws):
        """"""
        self.name = kws.get('brname', 'br-olan')
        self.tapname = kws.get('tapname', 'tap-olan')

        self._createBr(self.name)
        self.tap = self._createTap(self.tapname)
        self._addPort(self.name, self.tap.name)

        self.client = OpenTcpClient(gateway, port, **kws)

        self.idleTimeout = 5

    def _createBr(self, br, isup=True):
        """"""
        commands.getstatusoutput('brctl addbr %s' %br)
        return commands.getstatusoutput('ip link set %s up'%br)

    def _addPort(self, br, port):
        """"""
        return commands.getstatusoutput('brctl addif %s %s'%(br, port))

    def _createTap(self, name, isup=True):
        """"""
        tap = TunTapDevice(name=name, flags=IFF_TAP|IFF_NO_PI)
        if isup:
            tap.up()

        return tap

    def _readTap(self):
        """"""
        d = self.tap.read(self.tap.mtu+self.ETHLEN)
        logging.debug("receive from local %s", repr(d))
        self.client.sendMsg(d)

    def _readClient(self):
        """"""
        d = self.client.readMsg()
        logging.debug("receive from remote %s", repr(d))
    
        if d:
            self.tap.write(d)

    def tryconnect(self):
        """"""
        self.client.connect()

    def getsocks(self):
        """"""
        fds = [self.tap]
        if self.client.isok():
            fds.append(self.client.sock)

        return fds

    def loop(self):
        """"""
        while True:
            rs, _, es = select.select(self.getsocks(), [], [], self.idleTimeout)
            if len(rs) == 0 and len(es) == 0:
                self.tryconnect()
                continue

            for r in rs:
                if r is self.tap:
                    self._readTap()
                if r is self.client.sock:
                    self._readClient()

class System(object):
    """"""
    pidfile='/var/run/cpe.pid'

    def __init__(self, bridge):
        """"""
        signal.signal(signal.SIGINT, self.signal)
        signal.signal(signal.SIGTERM, self.signal)

        self.bridge = bridge

    def savepid(self):
        """"""
        with open(self.pidfile, 'w') as fp:
            fp.write(str(os.getpid()))

    def exit(self):
        """"""
        self.bridge.client.close()

    def signal(self, signum, frame):
        """"""
        logging.info("receive signal %s, %s", signum, frame)
        self.exit()

    def start(self):
        """"""
        self.savepid()
        self.bridge.loop()

def main():
    """"""
    opt = optparse.OptionParser()
    opt.add_option('-v', '--verbose', action="store_true", 
                   dest='verbose', default=False, help='enable verbose')
    opt.add_option('-g', '--gateway', action='store', 
                   dest='gateway', default='openlan.net', help='the address of ope connect to')
    opt.add_option('-p', '--port', action='store', 
                   dest='port', default=10001, help='the port of ope connect to')

    opts, _ = opt.parse_args()

    gateway = opts.gateway
    port    = int(opts.port)
    verbose = opts.verbose

    if verbose:
        basicConfig('../bridge.log', logging.DEBUG)
    else:
        basicConfig('../bridge.log', logging.INFO)

    br = Bridge(gateway, port, maxsize=1514)

    sysm = System(br)
    sysm.start()

if __name__ == '__main__':
    main()