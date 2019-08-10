'''
Created on Apr 4, 2019

@author: info
'''

import logging
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from libolan.ethernet import Ethernet
from .gateway import Gateway

class OpeRequestHandler(SimpleXMLRPCRequestHandler):
    ''''''
    def log_message(self, format, *args):
        """
        """
        logging.info("%s - - [%s] %s" %
                     (self.address_string(),
                      self.log_date_time_string(), 
                      format%args))
    
class OpeRpcApi(object):
    """"""
    def listCpe(self):
        """"""
        cpes = []
        server = Gateway.getServer()
        for conn in server.listConn():
            cpes.append({'host'    : conn.addr[0], 
                         'port'    : conn.addr[1],
                         'up_time' : str(conn.upTime()),
                         'socket'  : conn.fd(), 
                         'tx_drop' : str(conn.droperror),
                         'tx_byte' : str(conn.txbyte),
                         'rx_byte' : str(conn.rxbyte)})
        return cpes

    def listMac(self):
        """"""
        macs = []
        server = Gateway.getServer()
        for entry in server.fib.listEntry():
            macs.append({'eth'    : Ethernet.addr2Str(entry.ethdst),
                         'host'   : entry.conn.addr[0], 
                         'port'   : entry.conn.addr[1],
                         'up_time': str(entry.upTime())})
        return macs

class OpeRpcService(object):
    """"""
    def __init__(self, port=10081, addr="127.0.0.1", **kws):
        """"""
        self.port = port
        self.addr = addr  
   
        self.api = OpeRpcApi()
        self.server = SimpleXMLRPCServer((self.addr, self.port), requestHandler=OpeRequestHandler)
        self.server.register_instance(self.api)

    def start(self):
        """"""
        logging.info('listening rpc on *:%s', self.port)
        self.server.serve_forever()

if __name__ == '__main__':
    g = OpeRpcService()
    g.start()
