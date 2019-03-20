'''
Created on Feb 23, 2019

@author: info
'''

import optparse

opt = optparse.OptionParser()

def addOptions():
    """"""
    opt.add_option('-v', '--verbose', action="store_true", dest='verbose', 
                   default=False, help='enable verbose')
    opt.add_option('-g', '--gateway', action='store', dest='gateway', 
                   default='openlan.net', help='address of ope connect to, default <openlan.net>')
    opt.add_option('-r', '--rpcport', action='store', dest='xrpcport', 
                   default=5851, help='xmlrpc port of cpe connect to, default <5851>')
    opt.add_option('-P', '--pid', action='store',  dest='pid', 
                   default='/var/run/cpe', help='directory pid saved, default </var/run/cpe>')
    opt.add_option('-L', '--log', action='store', dest='log',
                   default='/var/log/cpe.log', help='file log saved, default </var/log/cpe.pid>')
    opt.add_option('-a', '--action', action="store", dest='action', 
                   default='status', help='action such as start, stop, restart')

def parseOptions():
    """"""
    return opt.parse_args()
