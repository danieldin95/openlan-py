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
    opt.add_option('-p', '--port', action='store', dest='port', 
                   default=5000, help='port of sky listen to')
    opt.add_option('-P', '--pid', action='store', dest='pid', 
                   default='/var/run/sky', help='directory pid saved')
    opt.add_option('-L', '--log', action='store', dest='log', 
                   default='/var/log/sky.log', help='file log saved')
    opt.add_option('-a', '--action', action="store", dest='action', 
                   default='status', help='action such as start, stop, restart')

def parseOptions():
    """"""
    return opt.parse_args()