'''
Created on Mar 6, 2019

@author: Daniel
'''

from SimpleXMLRPCServer import SimpleXMLRPCServer

class XMLRPCAPI(object):
    """"""
    def __init__(self, portmap=[]):
        """
        @param portmap: {'openPort': 10001} 
        """
        self.portmap = portmap
  
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

class XMLRPCServer(object):
    
    def __init__(self, addr='0.0.0.0', port=5851, portmap=[]):
        self.port = port
        self.addr = addr
        self.api = XMLRPCAPI(portmap)
        self.server = SimpleXMLRPCServer((self.addr, self.port))      
        self.server.register_instance(self.api)

    def start(self):
        logging.info('listening rpc on *:%s', self.port)
        self.server.serve_forever()        
