#!/usr/bin/env python

'''
Created on Feb 16, 2019

@author: info
'''

import sys
import commands
import select
import os
import signal

import pytun

from tcpClient import TcpClient

DEBUG = False

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

        self.DEBUG = kws.get('DEBUG', False)
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
        tap = pytun.TunTapDevice(name=name, flags=pytun.IFF_TAP|pytun.IFF_NO_PI)
        if isup:
            tap.up()

        return tap

    def _readTap(self):
        """"""
        d = self.tap.read(self.tap.mtu+self.ETHLEN)
        if self.DEBUG:
            print "receive frame from local %s" %(repr(d))
        self.client.sendMsg(d)

    def _readClient(self):
        """"""
        d = self.client.readMsg()
        if self.DEBUG:
            print "receive frame from remote %s" %(repr(d))
        if d:
            self.tap.write(d)

    def tryconnect(self):
        """"""
        self.client.connect()

    def getfds(self):
        """"""
        fds = [self.tap]
        if self.client.s:
            fds.append(self.client.s)

        return fds

    def loop(self):
        """"""
        while True:
            rs, ws, es = select.select(self.getfds(), [], [], self.idleTimeout)
            if len(rs) == 0 and len(es) == 0 and len(ws) == 0:
                self.tryconnect()
                continue

            for r in rs:
                if r is self.tap:
                    self._readTap()
                if r is self.client.s:
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
        print "receive signal %s, %s" %(signum, frame)
        self.exit()

    def start(self):
        """"""
        self.savepid()
        self.bridge.loop()

def main():
    """"""
    if len (sys.argv) == 3:
        gateway = sys.argv[1]
        port = int(sys.argv[2])
    elif len(sys.argv) == 2:
        gateway = sys.argv[1]
        port = 10001
    else:
        print('usage: bridge <gateway> <port>')
        return

    br = Bridge(gateway, port, DEBUG=DEBUG)

    sysm = System(br)
    sysm.start()

if __name__ == '__main__':
    main()