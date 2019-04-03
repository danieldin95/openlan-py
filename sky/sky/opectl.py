'''
Created on Feb 28, 2019

@author: info
'''

import xmlrpclib

class OpeCtl(object):
    """"""
    def __init__(self, connect_to="127.0.0.1:10081"):
        """"""
        self.connto = connect_to
        self.proxy  = xmlrpclib.ServerProxy("http://{0}/".format(self.connto))

    def listCpe(self):
        """"""
        return self.proxy.listCpe()

    def listMac(self):
        """"""
        return self.proxy.listMac()