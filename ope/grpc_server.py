'''
Created on Feb 25, 2019

@author: info
'''

from concurrent import futures
import time
import logging

import grpc

import ope_pb2
import ope_pb2_grpc

class OpeService(ope_pb2_grpc.OpeServicer):
    """"""
    def SayHi(self, request, context):
        """"""
        return ope_pb2.HiReply(message='Hello, %s!' % request.name)

    def GetCpe(self, request, context):
        """"""
        return ope_pb2.CpeReply(name='Get Cpe.')

class GrpcServer(object):
    """"""
    server = None

    @classmethod
    def run(cls):
        """"""
        cls.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
        ope_pb2_grpc.add_OpeServicer_to_server(OpeService(), cls.server)
        cls.server.add_insecure_port('[::]:50051')
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