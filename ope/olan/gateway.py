#!/usr/bin/env python

'''
Created on Feb 28, 2019

@author: Daniel
'''


import os
import signal
import logging

from libolan.log import basicConfig
from libolan.rwlock import RWLock

from .server import OpenServer
from .server import OpenTcpConn

class Gateway(object):
    """"""
    servers = {}
    rwlock = RWLock()

    def __init__(self, server):
        """"""
        self.server = server
        self.__class__.addServer(server)
        self.server.recvFunc  = self.forward

    def start(self):
        """"""
        self.server.loop()

    def forward(self, conn, m):
        """
        @param m: TcpMesg's instance. 
        """
        self.server.forward(conn, m)

    @classmethod
    def addServer(cls, server):
        """"""
        with cls.rwlock.writer_lock:
            if cls.servers.get(server.key) is None:
                cls.servers[server.key] = server

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
