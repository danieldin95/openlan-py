'''
Created on Mar 6, 2019

@author: info
'''

from SimpleXMLRPCServer import SimpleXMLRPCServer

def hi(name):
    """"""
    return 'Hi {0}'.format(name)


def start(port=8000, addr="0.0.0.0"):
    """"""
    server = SimpleXMLRPCServer((addr, port))
    server.register_function(hi, "hi")
    server.serve_forever()