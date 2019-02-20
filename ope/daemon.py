#!/usr/bin/env python

'''
Created on Feb 23, 2019

@author: info
'''

import logging

from lib.daemon import Daemon
from lib.log import basicConfig

from .options import addOptions
from .options import parseOptions

from .gateway import Gateway
from .gateway import OpenTcpConn
from .gateway import OpenServer

from .grpc_server import GrpcServer

class OpeDaemon(Daemon):
    """"""
    @classmethod
    def run(cls):
        """"""
        opts, _ = parseOptions()

        logging.info("starting {0}".format(cls.__name__))
        gw = Gateway(OpenServer(int(opts.port), tcpConn=OpenTcpConn))

        GrpcServer.run()
        gw.loop()

    @classmethod
    def sigtermHandler(cls, signo, frame):
        """"""
        logging.info("exiting from {0}".format(cls.__name__))

        GrpcServer.stop()

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