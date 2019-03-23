'''
Created on Feb 25, 2019

@author: Daniel
'''

import time
from threading import Thread
from SimpleXMLRPCServer import SimpleXMLRPCServer

from libolan.ethernet import Ethernet 

from .gateway import Gateway

class OpeService(object):
    """"""
    def __init__(self, port=5651, addr="0.0.0.0", **kws):
        """"""
        self.port = port
        self.addr = addr  
   
        self.server = SimpleXMLRPCServer((self.addr, self.port))
        self.register(self.listCpe, "listCpe")
        self.register(self.listMac, "listMac")
        
    def start(self):
        """"""
        self.server.serve_forever()
  
    def register(self, func, name):
        """"""
        self.server.register_function(func, name)
        
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
    
if __name__ == '__main__':
    g = OpeService()
    g.start()
    try:
        while True:
            time.sleep(3000)
    except KeyboardInterrupt:
        g.stop()
