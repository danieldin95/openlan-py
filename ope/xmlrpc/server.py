'''
Created on Feb 25, 2019

@author: Daniel
'''

import time
from SimpleXMLRPCServer import SimpleXMLRPCServer

from libolan.ethernet import Ethernet 
from .gateway import Gateway

class OpeXMLRPCAPI(object):
    """"""
    def listCpe(self):
        """"""
        cpes = []
        server = Gateway.getServer()
        for conn in server.listConn():
            cpes.append({'host':   conn.addr[0], 
                         'port':   conn.addr[1],
                         'up_time': conn.upTime(),
                         'socket':  conn.fd(), 
                         'tx_drop': conn.droperror,
                         'tx_byte': conn.txbyte,
                         'rx_byte': conn.rxbyte})
        return cpes

    def listMac(self):
        """"""
        fibs = []
        server = Gateway.getServer()
        for entry in server.fib.listEntry():
            fibs.append({'eth':  Ethernet.addr2Str(entry.ethdst),
                        'host': entry.conn.addr[0], 
                        'port': entry.conn.addr[1],
                        'up_time': entry.upTime()})
        return fibs
    
class OpeXMLRPCServer(object):
    """"""
    def __init__(self, port=5651, addr="127.0.0.1", **kws):
        """"""
        self.port = port
        self.addr = addr

        self.api = OpeXMLRPCAPI()
        self.server = SimpleXMLRPCServer((self.addr, self.port))      
        self.server.register_instance(self.api)

    def start(self):
        """"""
        self.server.serve_forever()

if __name__ == '__main__':
    g = OpeXMLRPCServer()
    g.start()
    try:
        while True:
            time.sleep(3000)
    except KeyboardInterrupt:
        g.stop()
