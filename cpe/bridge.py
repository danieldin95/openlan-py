#!/usr/bin/env python

'''
Created on Feb 16, 2019

@author: info
'''

import sys
import commands

import pytun

from tcpClient import TcpClient

class Bridge(object):
    """"""
    def __init__(self, gateway, port=10001, brname="br-olan", tapname="tap-olan"):
        """"""
        self.name = brname
        self.gateway = gateway
        self.tapname = tapname
        
        self._createBr(self.name)
        self.tap = self._createTap(self.tapname)
        self._addPort(self.name, self.tap.name)

        self.client = TcpClient(gateway, port)

    def _createBr(self, br, isup=True):
        """"""
        commands.getstatusoutput('brctl addbr %s' %br)
        return commands.getstatusoutput('ip link set %s up'%br)

    def _addPort(self, br, port):
        """"""
        return commands.getstatusoutput('brctl addif %s %s'%(br, port))

    def _createTap(self, name, isup=True):
        """"""
        tap = pytun.TunTapDevice(name=name, flags=pytun.IFF_TAP)
        if isup:
            tap.up()

        return tap

    def tryconnect(self):
        """"""
        self.client.connect()

    def loop(self):
        """"""
        self.tryconnect()
        while True:
            d = self.tap.read(self.tap.mtu)
            print "receive frame %s" %(repr(d))
            self.client.sendMsg(d[4:])

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

    br = Bridge(gateway, port)
    br.loop()

if __name__ == '__main__':
    main()