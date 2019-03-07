'''
Created on Mar 6, 2019

@author: info
'''
from .gateway import Gateway

from SimpleXMLRPCServer import SimpleXMLRPCServer

def hi(name):
    """"""
    return 'Hi {0}'.format(name)

def listPort():
    """"""
    servers = []
    for server in Gateway.listServer():
        servers.append(server.port)

    return servers

class XmlRpcServer(object):
    """"""

    def __init__(self, port=8000, addr="0.0.0.0"):
        """"""
        self.port = port
        self.addr = addr
        
        self.server = SimpleXMLRPCServer((self.addr, self.port))
        self.server.register_function(hi, "hi")
        self.server.register_function(listPort, "listPort")
  
    def start(self, port=8000, addr="0.0.0.0"):
        """"""
        self.server.serve_forever()
  
    def register(self, func, name):
        """"""
        self.server.register_function(func, name)
  
