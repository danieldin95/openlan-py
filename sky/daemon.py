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
from .sky.app import start

class OpeDaemon(Daemon):
    """"""
    @classmethod
    def run(cls):
        """"""
#         opts, _ = parseOptions()

        logging.info("starting {0}".format(cls.__name__))
        start()

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