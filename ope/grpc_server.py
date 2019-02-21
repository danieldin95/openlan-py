'''
Created on Feb 25, 2019

@author: info
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
    server = None

    @classmethod
    def run(cls, port=5051, addr='127.0.0.1', maxWorkers=10):
        """"""
        cls.server = grpc.server(futures.ThreadPoolExecutor(max_workers=maxWorkers))

        ope_pb2_grpc.add_OpeServicer_to_server(OpeService(), cls.server)
        cls.server.add_insecure_port('{0}:{1}'.format(addr, port))
        cls.server.start()

        return cls.server

    @classmethod
    def stop(cls):
        """"""
        if cls.server is None:
            return 

        cls.server.stop(0)
        cls.server = None

if __name__ == '__main__':
    GrpcServer.run()
    try:
        while True:
            time.sleep(3000)
    except KeyboardInterrupt:
        GrpcServer.stop()