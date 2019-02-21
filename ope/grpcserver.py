'''
Created on Feb 25, 2019

@author: Daniel
'''

from concurrent import futures
import time
import grpc

from lib.ethernet import Ethernet 

from . import ope_pb2
from . import ope_pb2_grpc

from .gateway import Gateway

class OpeService(ope_pb2_grpc.OpeServicer):
    """"""
    def SayHi(self, request, context):
        """"""
        return ope_pb2.HiReply(message = 'Hi, {0}'.format(request.name))

    def GetCpe(self, request, context):
        """"""
        server = Gateway.getServer()
        for conn in server.listConn():
            yield ope_pb2.CpeReply(host    = conn.addr[0], 
                                   port    = conn.addr[1],
                                   up_time = str(conn.upTime()),
                                   socket  = conn.fd(), 
                                   tx_drop = conn.droperror,
                                   tx_byte = conn.txbyte,
                                   rx_byte = conn.rxbyte)

    def GetFib(self, request, context):
        """"""
        server = Gateway.getServer()
        for entry in server.fib.listEntry():
            yield ope_pb2.FibReply(eth     = Ethernet.addr2Str(entry.ethdst),
                                   host    = entry.conn.addr[0], 
                                   port    = entry.conn.addr[1],
                                   up_time = str(entry.upTime()))

class GrpcServer(object):
    """"""
 
    def __init__(self, port=5051, addr='127.0.0.1', maxWorkers=10):
        """"""
        self.addr = addr
        self.port = port
        self.maxWorkers = maxWorkers
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=self.maxWorkers))

    def start(self):
        """"""
        ope_pb2_grpc.add_OpeServicer_to_server(OpeService(), self.server)
        self.server.add_insecure_port('{0}:{1}'.format(self.addr, self.port))
        self.server.start()

    def stop(self):
        """"""
        if self.server is None:
            return 

        self.server.stop(0)
        self.server = None

if __name__ == '__main__':
    g = GrpcServer()
    g.start()
    try:
        while True:
            time.sleep(3000)
    except KeyboardInterrupt:
        g.stop()
