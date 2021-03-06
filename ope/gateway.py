#!/usr/bin/env python

'''
Created on Feb 28, 2019

@author: info
'''


import os
import signal
import logging

from libolan.log import basicConfig

from .options import addOptions
from .options import parseOptions
from ope.openserver import OpenServer
from ope.openserver import OpenTcpConn

class Gateway(object):
    """"""
    servers = {}

    def __init__(self, server):
        """"""
        self.server = server
        self.__class__.addServer(server)
        self.server.recvFunc  = self.forward

    def loop(self):
        """"""
        self.server.loop()

    def forward(self, m):
        """"""
        self.server.forward(m)

    @classmethod
    def addServer(cls, server):
        """"""
        if cls.servers.get(server.key) is None:
            cls.servers[server.key] = server
     
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
