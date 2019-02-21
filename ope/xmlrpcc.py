'''
Created on Mar 6, 2019

@author: info
'''

import xmlrpclib

if __name__ == '__main__':

    proxy = xmlrpclib.ServerProxy("http://localhost:8000/")
    print "listPort {0}".format(proxy.listPort())