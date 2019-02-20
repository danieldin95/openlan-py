
import grpc

from ope import ope_pb2
from ope import ope_pb2_grpc

from flask import Flask
app = Flask(__name__)

def getCpe(to='127.0.0.1:50051'):
    """"""
    cpes = []

    with grpc.insecure_channel(to) as channel:
        stub = ope_pb2_grpc.OpeStub(channel)
        for cpe in stub.GetCpe(ope_pb2.CpeRequest(name='all')):
            cpes.append(cpe)

    return cpes

@app.route('/')
def index():
    """"""
    resp = ''
    for cpe in getCpe():
        resp += '<li>{0}</li>'.format(cpe)

    return '<ol>{0}</ol>'.format(resp)

def start(host='0.0.0.0'):
    """"""
    app.run(host)

if __name__ == '__main__':
    start()
