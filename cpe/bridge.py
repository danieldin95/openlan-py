#!/usr/bin/env python

'''
Created on Feb 16, 2019

@author: Daniel
'''

import select
import os
import signal
import logging
import struct

from .options import addOptions
from .options import parseOptions
from .openclient import OpenTcpClient

from libolan.log import basicConfig
from libolan.util import call
from libolan.tcpmesg import TcpMesg

from libdynload.pytun import TunTapDevice
from libdynload.pytun import IFF_TAP
from libdynload.pytun import IFF_NO_PI

class Bridge(object):
    """"""
    ETHLEN = 14

    def __init__(self, gateway, ports=[5551], **kws):
        """"""
        self.name = kws.get('brname', 'br-olan')
        self.tapname = kws.get('tapname', 'tap-olan')

        ret, out, _ = self._createBr(self.name)
        if ret != 0:
            raise RuntimeError('{0}'.format(out)) 

        self.tap = self._createTap(self.tapname)
        ret, out, _ = self._addPort(self.name, self.tap.name)
        if ret != 0:
            raise RuntimeError('{0}'.format(out)) 

        self.sysid = struct.unpack('!I', self.tap.hwaddr[2:])[0]
        self.zone  = 0

        self.clients = {}
        for port in ports:
            c = OpenTcpClient(self.sysid, self.zone, gateway, port, **kws)
            self.clients[c.key] = c
        
        self.socks = {}
        
        self.idleTimeout = 5
        self.curClient   = 0

    def _createBr(self, br):
        """"""
        ret, out, err = call(['brctl', 'addbr', br])
        if ret != 0 and out.find('already exists')  == -1:
            return ret, out, err

        return call(['ip', 'link', 'set', br, 'up'])

    def _addPort(self, br, port):
        """"""
        return call(['brctl', 'addif', br, port])

    def _createTap(self, name, isup=True):
        """"""
        tap = TunTapDevice(name=name, flags=IFF_TAP|IFF_NO_PI)
        if isup:
            tap.up()

        return tap

    def _sendMsg(self, data):
        """"""
        if self.curClient == len(self.clients):
            self.curClient = 0

        logging.debug('curClient %d', self.curClient)
        self.clients.values()[self.curClient].sendMsg(data)
        self.curClient += 1

    def _readTap(self):
        """"""
        d = self.tap.read(self.tap.mtu+self.ETHLEN)
        logging.debug("receive from local %s", repr(d))
        self._sendMsg(d)

    def _readClient(self, sock):
        """"""
        client = self.socks.get(sock)
        if client is None:
            logging.error("read client for %s not found", str(sock))
            return

        d = client.readMsg()
        if d:
            m = TcpMesg.unpack(d)
            logging.debug("receive from remote %s %s", client.sock.fileno(), m)
            if m.data:
                self.tap.write(m.data)

    def _closeClient(self, sock):
        """"""
        logging.warn("close client(%d)", sock.fileno())
        client = self.clients.get(sock)
        if client is None:
            return

        client.close()

    def tryconnect(self):
        """"""
        for client in self.clients.values():
            client.connect()

    def close(self):
        """"""
        for client in self.clients.values():
            client.close()

    def getsocks(self):
        """"""
        self.socks = {self.tap:self.tap}

        for client in self.clients.values():
            if not client.isok():
                client.connect()

            if client.isok():
                self.socks[client.sock] = client

        return self.socks.keys()

    def loop(self):
        """"""
        self.tryconnect()

        while True:
            self.socks = {}
            self.getsocks()
            
            rs, _, es = select.select(self.socks.keys(), [], self.socks.keys(), self.idleTimeout)
            if len(rs) == 0 and len(es) == 0:
                self.tryconnect()
                continue

            for r in rs:
                if r is self.tap:
                    self._readTap()
                else:
                    self._readClient(r)

            for e in es:
                if e is self.tap:
                    raise RuntimeError("tap device has error")
                else:
                    self._closeClient(r)

class System(object):
    """"""
    def __init__(self, bridge, **kws):
        """"""
        signal.signal(signal.SIGINT, self.signal)
        signal.signal(signal.SIGTERM, self.signal)
        signal.signal(signal.SIGKILL, self.signal)
        signal.signal(signal.SIGABRT, self.signal)

        self.bridge = bridge
        self.pidfile = kws.get('pidfile', '/var/run/cpe.pid')

    def savepid(self):
        """"""
        with open(self.pidfile, 'w') as fp:
            fp.write(str(os.getpid()))

    def exit(self):
        """"""
        self.bridge.close()

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
    addOptions()
    opts, _ = parseOptions()

    gateway = opts.gateway
    port    = int(opts.port)
    verbose = opts.verbose

    if verbose:
        basicConfig(opts.log, logging.DEBUG)
    else:
        basicConfig(opts.log, logging.INFO)

    br = Bridge(gateway, [port], maxsize=1514)

    sysm = System(br, pidfile=opts.pid)
    sysm.start()

if __name__ == '__main__':
    main()
