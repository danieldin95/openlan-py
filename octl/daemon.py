#!/usr/bin/env python

'''
Created on Feb 23, 2019

@author: Daniel
'''

import logging

from libolan.daemon import Daemon
from libolan.log import basicConfig

from .options import addOptions
from .options import parseOptions

class OctlDaemon(Daemon):
    """"""
    @classmethod
    def run(cls, pidfile, **kws):
        """"""
        opts, _ = parseOptions

        logging.info("starting {0}".format(cls.__name__))

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
        OctlDaemon.start(opts.pid)
    elif opts.action == 'stop':
        OctlDaemon.stop(opts.pid)
    elif opts.action == 'restart':
        OctlDaemon.restart(opts.pid)
    else:
        print OctlDaemon.status(opts.pid)

if __name__ == '__main__':
    main()
