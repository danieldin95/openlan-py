'''
Created on Mar 6, 2019

@author: info
'''
from .gateway import Gateway

from SimpleXMLRPCServer import SimpleXMLRPCServer

class XmlRpcServer(object):
    """"""

    def __init__(self, port=8000, addr="0.0.0.0", **kws):
        """"""
        self.port = port
        self.addr = addr  
        self.portmap = kws.get('portmap', [])
   
        self.server = SimpleXMLRPCServer((self.addr, self.port))
        self.register(self.hi, "hi")
        self.register(self.listPort, "listPort")
  
    def start(self):
        """"""
        self.server.serve_forever()
  
    def register(self, func, name):
        """"""
        self.server.register_function(func, name)

    def hi(self, name):
        """"""
        return 'Hi {0}'.format(name)

    def listPort(self):
        """"""
        ports = []
        for p in self.portmap:
            port = p.get('openPort')
            if port is None:
                continue
   
            ports.append(port)

        return ports
  
