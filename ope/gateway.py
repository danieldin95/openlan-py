#!/usr/bin/env python

'''
Created on Feb 28, 2019

@author: info
'''


import os
import signal
import logging

from lib.log import basicConfig
from lib.rwlock import RWLock

from .options import addOptions
from .options import parseOptions
from .openserver import OpenServer
from .openserver import OpenTcpConn

class Gateway(object):
    """"""
    servers = {}
    rwlock = RWLock()

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
        with cls.rwlock.writer_lock:
            if cls.servers.get(server.key()) is None:
                cls.servers[server.key()] = server

    @classmethod
    def getServer(cls, key=None):
        """"""
        if key is None:
            with cls.rwlock.reader_lock:
                if len(cls.servers) > 0: 
                    return cls.servers.values()[0]

            return None

        return cls.servers.get(key)

    @classmethod
    def listServer(cls):
        """"""
        with cls.rwlock.reader_lock:
            for server in cls.servers.values():
                yield server

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
