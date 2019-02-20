'''
Created on Feb 25, 2019

@author: info
'''

import grpc

from . import ope_pb2
from . import ope_pb2_grpc

def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = ope_pb2_grpc.OpeStub(channel)
        response = stub.SayHi(ope_pb2.HiRequest(name='you'))
        
        for cpe in stub.GetCpe(ope_pb2.CpeRequest(host='')):
            print cpe

        for fib in stub.GetFib(ope_pb2.FibRequest(host='')):
            print fib

    print response

if __name__ == '__main__':
    run()
