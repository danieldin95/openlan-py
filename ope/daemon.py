#!/usr/bin/env python

'''
Created on Feb 23, 2019

@author: info
'''

import logging
import time

from multiprocessing import Process

from lib.daemon import Daemon
from lib.log import basicConfig

from .options import addOptions
from .options import parseOptions

from .gateway import Gateway
from .gateway import OpenTcpConn
from .gateway import OpenServer

from .grpcserver import GrpcServer
from .xmlrpc import XmlRpcServer

class OpeDaemon(Daemon):
    """"""
    GRPC_PORT = 5051

    @classmethod
    def run(cls, pidpath):
        """"""
        opts, _ = parseOptions()
        
        logging.info("starting {0}".format(cls.__name__))
        
        def _start_one_gateway(open_port, grpc_port):
            """"""
            cls.savePid(pidpath)
            grpc = GrpcServer(grpc_port)
            grpc.start()
  
            gw = Gateway(OpenServer(open_port, tcpConn=OpenTcpConn))
            gw.loop()

        portmap = []
        port = int(opts.port)
        for i in range(0, int(opts.multiple)):
            open = port+i
            grpc = cls.GRPC_PORT+i
            portmap.append({'openPort': open, 'grpcPort': grpc})
            p = Process(target=_start_one_gateway, args=(open, grpc))
            p.start()

        xmlrpc = XmlRpcServer(portmap=portmap)
        xmlrpc.start()

    @classmethod
    def sigtermHandler(cls, signo, frame):
        """"""
        logging.info("exiting from {0}".format(cls.__name__))

        raise SystemExit(253)

def main():
    """"""
    addOptions()

    opts, _ = parseOptions()

    if opts.verbose:
        basicConfig(opts.log, logging.DEBUG)
    else:
        basicConfig(opts.log, logging.INFO)

    if opts.action == 'start':
        OpeDaemon.start(opts.pid)
    elif opts.action == 'stop':
        OpeDaemon.stop(opts.pid)
    elif opts.action == 'restart':
        OpeDaemon.restart(opts.pid)
    else:
        print OpeDaemon.status(opts.pid)

if __name__ == '__main__':
    main()
