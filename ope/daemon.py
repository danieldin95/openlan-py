#!/usr/bin/env python

'''
Created on Feb 23, 2019

@author: info
'''

import logging
from threading import Thread
from libolan.daemon import Daemon
from libolan.log import basicConfig

from .options import addOptions
from .options import parseOptions

from .gateway import Gateway
from .gateway import OpenTcpConn
from .gateway import OpenServer
from .xmlrpcs import OpeRpcService

class OpeDaemon(Daemon):
    """"""
    @classmethod
    def run(cls):
        """"""
        opts, _ = parseOptions()

        logging.info("starting {0}".format(cls.__name__))

        rpc = OpeRpcService()
        gw = Gateway(OpenServer(int(opts.port), tcpConn=OpenTcpConn))

        t1 = Thread(target=rpc.start)
        t1.start()

        t2 = Thread(target=gw.loop)
        t2.start()

        t1.join()
        t2.join()
                
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
