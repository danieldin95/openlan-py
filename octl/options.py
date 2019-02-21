'''
Created on Feb 16, 2019

@author: Daniel
'''

import optparse

opt = optparse.OptionParser()

def addOptions():
    """"""
    opt.add_option('-v', '--verbose', action="store_true", 
                   dest='verbose', default=False, help='enable verbose')
    opt.add_option('-p', '--port', action='store', 
                   dest='port', default=5550, help='port of open controller listen to')
    opt.add_option('-P', '--pid', action='store', 
                   dest='pid', default='/var/run/octl', help='file pid saved')
    opt.add_option('-L', '--log', action='store', 
                   dest='log', default='/var/log/octl.log', help='file log saved')
    opt.add_option('-a', '--action', action="store", 
                   dest='action', default='status', help='action include start, stop, restart.')

def parseOptions():
    """"""
    return opt.parse_args()
