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

from tcpClient import TcpClient
from lib.log import basicConfig

def addlibdy():
    """"""
    libdir = os.path.dirname(__file__)+'/../lib-dynload'
    sys.path.append(libdir)

addlibdy()

from pytun import TunTapDevice, IFF_TAP, IFF_NO_PI

class Bridge(object):
    """"""
    ETHLEN = 14
    
    def __init__(self, gateway, port=10001, brname="br-olan", tapname="tap-olan", **kws):
        """"""
        self.name = brname
        self.gateway = gateway
        self.tapname = tapname
        
        self._createBr(self.name)
        self.tap = self._createTap(self.tapname)
        self._addPort(self.name, self.tap.name)

        self.client = TcpClient(gateway, port, **kws)

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
        basicConfig('bridge.log', logging.DEBUG)
    else:
        basicConfig('bridge.log', logging.INFO)

    br = Bridge(gateway, port, maxsize=1514)

    sysm = System(br)
    sysm.start()

if __name__ == '__main__':
    main()