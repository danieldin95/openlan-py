#!/usr/bin/env python

'''
Created on Feb 23, 2019

@author: info
'''

import logging

from lib.daemon import Daemon
from lib.log import basicConfig

from options import addOptions
from options import parseOptions

from gateway import Gateway
from gateway import OpenTcpConn
from gateway import OpenServer

class OpeDaemon(Daemon):
    """"""
    def run(self):
        """"""
        opts, _ = parseOptions()

        logging.info("starting {0}".format(self.__class__.__name__))

        Gateway(OpenServer(int(opts.port), tcpConn=OpenTcpConn)).loop()

def main():
    """"""
    addOptions()

    opts, _ = parseOptions()

    if opts.verbose:
        basicConfig(opts.log, logging.DEBUG)
    else:
        basicConfig(opts.log, logging.INFO)

    daemon = OpeDaemon(pidfile=opts.pid)

    if opts.action == 'start':
        daemon.start()
    elif opts.action == 'stop':
        daemon.stop()
    elif opts.action == 'restart':
        daemon.restart()
    else:
        print daemon.status()

if __name__ == '__main__':
    main()