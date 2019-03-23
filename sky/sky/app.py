'''
Created on Feb 28, 2019

@author: info
'''

from flask import Flask
from flask import render_template

from .opectl import OpeCtl

opectl = OpeCtl() 
app = Flask(__name__)

@app.route('/')
def index():
    """"""
    cpes = opectl.listCpe()
    macs = opectl.listMac()

    return render_template('index.html', cpes=cpes, fibs=macs)

def start(host='0.0.0.0', port=5000):
    """"""
    app.run(host, port)

if __name__ == '__main__':
    start()
