'''
Created on Feb 23, 2019

@author: info
'''

import optparse

opt = optparse.OptionParser()

def addOptions():
    """"""
    opt.add_option('-v', '--verbose', action="store_true", 
                   dest='verbose', default=False, help='enable verbose')
    opt.add_option('-p', '--port', action='store', 
                   dest='port', default=10001, help='the port of ope connect to')
    opt.add_option('-P', '--pid', action='store', 
                   dest='pid', default='/var/run/ope.pid', help='the file pid saved')
    opt.add_option('-L', '--log', action='store', 
                   dest='log', default='/var/log/ope.log', help='the file log saved')
    opt.add_option('-a', '--action', action="store", 
                   dest='action', default='status', help='the action include start, stop, restart.')

def parseOptions():
    """"""
    return opt.parse_args()