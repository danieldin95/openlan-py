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
    @classmethod
    def run(cls, port=8000, addr="0.0.0.0"):
        """"""
        server = SimpleXMLRPCServer((addr, port))
    
        server.register_function(hi, "hi")
        server.register_function(listPort, "listPort")
        
        server.serve_forever()