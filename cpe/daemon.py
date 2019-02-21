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

from .bridge import Bridge

class CpeDaemon(Daemon):
    """"""
    @classmethod
    def run(cls, pidfile):
        """"""
        opts, _ = parseOptions()

        logging.info("starting {0}".format(cls.__name__))

        Bridge(opts.gateway, int(opts.port), maxsize=1514).loop()

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