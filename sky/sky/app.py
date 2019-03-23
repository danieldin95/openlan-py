'''
Created on Feb 28, 2019

@author: info
'''

from flask import Flask
from flask import render_template
from flask import request

from .opectl import OpeCtl

app = Flask(__name__)

@app.route('/')
def index():
    """"""
    port = request.args.get('port', 5651)
    opectl = OpeCtl('127.0.0.1:{0}'.format(port))

    cpes = opectl.listCpe()
    macs = opectl.listMac()

    return render_template('index.html', cpes=cpes, fibs=macs)

def start(host='0.0.0.0', port=5000):
    """"""
    app.run(host, port)

if __name__ == '__main__':
    start()
