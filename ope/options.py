'''
Created on Feb 23, 2019

@author: Daniel
'''

import optparse

opt = optparse.OptionParser()

def addOptions():
    """"""
    opt.add_option('-v', '--verbose', action="store_true", dest='verbose', 
                   default=False, help="enable verbose")
    opt.add_option('-p', '--port', action='store', dest='port', 
                   default=5551, help='port of ope listen on, default <5551>')
    opt.add_option('-s', '--serviceport', action='store', dest='serviceport', 
                   default=5651, help='service port of ope listen on, default <5651>')
    opt.add_option('-r', '--rpcport', action='store', dest='xrpcport', 
                   default=5851, help='xmlrpc port of ope listen on, default <5851>')
    opt.add_option('-m', '--multiple', action='store', dest='multiple', 
                   default=1, help='number of processing, default <1>')
    opt.add_option('-P', '--pid', action='store', dest='pid', 
                   default='/var/run/ope', help="directory pid saved, default </var/run/ope>")
    opt.add_option('-L', '--log', action='store', dest='log', 
                   default='/var/log/ope.log', help="file log saved, default </var/log/ope.log>")
    opt.add_option('-a', '--action', action="store", dest='action',
                   default='status', help='action such start, stop, restart')

def parseOptions():
    """"""
    return opt.parse_args()
