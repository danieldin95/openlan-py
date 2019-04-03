'''
Created on Mar 6, 2019

@author: Daniel
'''

import xmlrpclib

if __name__ == '__main__':
    proxy = xmlrpclib.ServerProxy("http://localhost:10081/")
    print proxy.listCpe()
    print proxy.listMac()
