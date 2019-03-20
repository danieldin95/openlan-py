#!/usr/bin/env python

'''
Created on Feb 23, 2019

@author: Daniel
'''

import logging

from multiprocessing import Process

from libolan.daemon import Daemon
from libolan.log import basicConfig

from .options import addOptions
from .options import parseOptions

from .gateway import Gateway
from .gateway import OpenTcpConn
from .gateway import OpenServer

from .service import OpeService
from .xmlrpc import XmlRpcServer

class OpeDaemon(Daemon):
    """"""
    @classmethod
    def run(cls, pidpath):
        """"""
        opts, _ = parseOptions()
        
        logging.info("starting {0}".format(cls.__name__))

        def _start_one_gateway(open_port, grpc_port):
            """"""
            cls.savePid(pidpath)
            rpc = OpeService(grpc_port)
            rpc.start()
  
            gw = Gateway(OpenServer(open_port, tcpConn=OpenTcpConn))
            gw.loop()

        portmap = []
        for i in range(0, int(opts.multiple)):
            _open = int(opts.port)+i
            _grpc = int(opts.grpcport)+i
            portmap.append({'openPort': _open, 'grpcPort': _grpc})
            p = Process(target=_start_one_gateway, args=(_open, _grpc))
            p.start()

        xmlrpc = XmlRpcServer(port=int(opts.xrpcport), portmap=portmap)
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
