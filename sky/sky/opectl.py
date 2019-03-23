'''
Created on Feb 28, 2019

@author: info
'''

import xmlrpclib

class OpeCtl(object):
    """"""
    def __init__(self, connect_to="127.0.0.1:5851"):
        """"""
        self.connectto = connect_to
        self.rpcproxy   = xmlrpclib.ServerProxy("http://{0}/".format(self.connectto))

    def listCpe(self):
        """"""
        return self.rpcproxy.listCpe()

    def listMac(self):
        """"""
        return self.rpcproxy.listMac()