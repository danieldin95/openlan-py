#!/usr/bin/env python

'''
Created on Feb 23, 2019

@author: Daniel
'''

import logging
import xmlrpclib
import socket

from libolan.daemon import Daemon
from libolan.log import basicConfig

from .options import addOptions
from .options import parseOptions

from .bridge import Bridge

class CpeDaemon(Daemon):
    """"""
    @classmethod
    def run(cls, pidfile):
        """"""
        opts, _ = parseOptions()
        proxy = xmlrpclib.ServerProxy("http://{0}:{1}/".format(opts.gateway, opts.xrpcport))
        
        try:
            ports = proxy.listPort()
        except socket.error as e:
            logging.error("starting {0} with {1}".format(cls.__name__, e))
            return 

        logging.info("starting {0}".format(cls.__name__))

        Bridge(opts.gateway, ports, maxsize=4096).loop()

def main():
    """"""
    addOptions()

    opts, _ = parseOptions()

    if opts.verbose:
        basicConfig(opts.log, logging.DEBUG)
    else:
        basicConfig(opts.log, logging.INFO)

    if opts.action == 'start':
        CpeDaemon.start(opts.pid)
    elif opts.action == 'stop':
        CpeDaemon.stop(opts.pid)
    elif opts.action == 'restart':
        CpeDaemon.restart(opts.pid)
    else:
        print CpeDaemon.status(opts.pid)

if __name__ == '__main__':
    main()
