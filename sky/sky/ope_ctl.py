'''
Created on Feb 28, 2019

@author: info
'''

import grpc
import sys

from ope import ope_pb2
from ope import ope_pb2_grpc

def getCpe(to='127.0.0.1:50051'):
    """"""
    cpes = []

    with grpc.insecure_channel(to) as channel:
        stub = ope_pb2_grpc.OpeStub(channel)
        for cpe in stub.GetCpe(ope_pb2.CpeRequest(name='all')):
            cpes.append(cpe)

    return cpes

class OpeCtl(object):
    """"""
    def __init__(self, connect_to="127.0.0.1:50051"):
        """"""
        self.connect_to = connect_to
        self.channel    = grpc.insecure_channel(self.connect_to)
        self.stub       = ope_pb2_grpc.OpeStub(self.channel)

    def getCpe(self):
        """"""
        return self.stub.GetCpe(ope_pb2.CpeRequest(host='all'))
    
    def getFib(self):
        """"""
        return self.stub.GetFib(ope_pb2.FibRequest(host='all'))