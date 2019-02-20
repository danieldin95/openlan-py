'''
Created on Feb 28, 2019

@author: info
'''

from flask import Flask
from flask import render_template

from .ope_ctl import OpeCtl

opectl = OpeCtl() 
app = Flask(__name__)

@app.route('/')
def index():
    """"""
    cpes = opectl.getCpe()
    fibs = opectl.getFib()

    return render_template('index.html', cpes=cpes, fibs=fibs)

def start(host='0.0.0.0', port=5000):
    """"""
    app.run(host, port)

if __name__ == '__main__':
    start()
